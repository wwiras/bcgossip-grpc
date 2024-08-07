from kubernetes import client, config
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
import json
import time
import logging
import subprocess  # For running ping or other latency measurement tools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):
        self.pod_name = socket.gethostname()
        self.host = socket.gethostbyname(self.pod_name)
        self.port = '5050'
        self.service_name = service_name

        # Load the topology from the ConfigMap
        with open('/app/config/network_topology.json', 'r') as f:
            self.topology = json.load(f)

        # Find neighbors based on the topology (without measuring latency yet)
        self.neighbor_pod_names = self._find_neighbors(self.pod_name)
        print(f"{self.pod_name}({self.host}) neighbors: {self.neighbor_pod_names}", flush=True)

        self.received_messages = set()

        self.gossip_initiated = False
        self.initial_gossip_timestamp = None

        # Dictionaries to track latency, message sizes, and transfer times (initialized empty)
        self.neighbor_latencies = {}
        self.neighbor_message_sizes = {}
        self.neighbor_transfer_times = {}

    def get_pod_ip(self, pod_name, namespace="default"):
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip

    def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id
        received_timestamp = time.time_ns()

        # Check for message initiation and set the initial timestamp
        if sender_id == self.pod_name and not self.gossip_initiated:
            self.gossip_initiated = True
            self.initial_gossip_timestamp = received_timestamp
            log_message = f"Gossip initiated by {self.pod_name}({self.host}) at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(received_timestamp / 1e9))}"
            self._log_event(message, sender_id, received_timestamp, None, 'initiate', log_message)

        # Check for duplicate messages
        elif message in self.received_messages:
            log_message = f"{self.pod_name}({self.host}) ignoring duplicate message: '{message}' from {sender_id}"
            self._log_event(message, sender_id, received_timestamp, None, 'duplicate', log_message)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by {self.pod_name}({self.host})")

        else:
            self.received_messages.add(message)
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            message_size = len(request.message)

            # Update neighbor latency, message size, and transfer time
            self.neighbor_latencies[sender_id] = propagation_time
            self.neighbor_message_sizes[sender_id] = message_size
            self.neighbor_transfer_times[sender_id] = propagation_time

            log_message = f"{self.pod_name}({self.host}) received: '{message}' from {sender_id} in {propagation_time:.2f} ms"
            self._log_event(message, sender_id, received_timestamp, propagation_time, 'received', log_message)

        # Gossip to neighbors
        self.gossip_message(message, sender_id, received_timestamp)
        return gossip_pb2.Acknowledgment(details=f"{self.pod_name}({self.host}) processed message: '{message}'")

    def gossip_message(self, message, sender_id, received_timestamp):
        # Calculate neighbor weights before gossiping
        self.calculate_neighbor_weights(sender_id)

        # Prioritize neighbors with higher weights
        sorted_neighbors = sorted(self.neighbors, key=lambda x: x[1], reverse=True)

        for neighbor_pod_name, _ in sorted_neighbors:
            if neighbor_pod_name != sender_id:
                neighbor_ip = self.get_pod_ip(neighbor_pod_name)
                target = f"{neighbor_ip}:5050"
                with grpc.insecure_channel(target) as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(
                            message=message,
                            sender_id=self.pod_name,
                            timestamp=received_timestamp
                        ))
                        print(
                            f"{self.pod_name}({self.host}) forwarded message: '{message}' to {neighbor_pod_name} ({neighbor_ip})",
                            flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message: '{message}' to {neighbor_pod_name}: {e}", flush=True)

    def _find_neighbors(self, node_id):
        """Identifies the neighbors of the given node based on the topology."""
        neighbors = []
        for link in self.topology['links']:
            if link['source'] == node_id:
                neighbors.append(link['target'])
            elif link['target'] == node_id:
                neighbors.append(link['source'])
        return neighbors

    def calculate_neighbor_weights(self, exclude_sender=None):
        """
        Calculates weights for neighbors based on latency and/or bandwidth, excluding the sender.
        """
        self.neighbors = []
        for neighbor_pod_name in self.neighbor_pod_names:
            if neighbor_pod_name == exclude_sender:
                continue  # Skip the sender

            latency = self.measure_latency(neighbor_pod_name)
            bandwidth = self.measure_bandwidth(neighbor_pod_name)

            # Calculate the weight using latency and bandwidth
            weight = self._calculate_weight(latency, bandwidth)

            self.neighbors.append((neighbor_pod_name, weight))

    def measure_latency(self, neighbor_pod_name):
        """
        Measures latency to a neighbor using the Ping RPC.
        """
        try:
            neighbor_ip = self.get_pod_ip(neighbor_pod_name)
            target = f"{neighbor_ip}:5050"
            with grpc.insecure_channel(target) as channel:
                stub = gossip_pb2_grpc.GossipServiceStub(channel)

                start_time = time.time_ns()
                response = stub.Ping(gossip_pb2.PingRequest())
                end_time = time.time_ns()

                round_trip_time = (end_time - start_time - (end_time - response.timestamp)) / 1e6  # in milliseconds
                return round_trip_time

        except grpc.RpcError as e:
            logging.error(f"Error measuring latency to {neighbor_pod_name}: {e}")
            return None

    def measure_bandwidth(self, neighbor_pod_name, payload_size_bytes=1024 * 1024):
        """
        Measures bandwidth to a neighbor using the MeasureBandwidth RPC.
        """
        try:
            neighbor_ip = self.get_pod_ip(neighbor_pod_name)
            target = f"{neighbor_ip}:5050"
            with grpc.insecure_channel(target) as channel:
                stub = gossip_pb2_grpc.GossipServiceStub(channel)
                response = stub.MeasureBandwidth(gossip_pb2.BandwidthRequest(payload_size=payload_size_bytes))
                return response.bandwidth_mbps
        except Exception as e:
            print(f"An unexpected error occurred: {e}", flush=True)

    def start_server(self):
        """
        Starts the gRPC server to listen for incoming requests.
        """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.pod_name}({self.host}) listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()  # Keep the server running


def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()


if __name__ == '__main__':
    run_server()
