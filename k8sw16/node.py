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
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):

        self.pod_name = socket.gethostname()
        self.host = socket.gethostbyname(self.pod_name)
        self.port = '5050'
        self.service_name = service_name

        # Load the topology from the "topology" or "topology_kmeans" folder
        # if os.environ['CLUSTER'] == 0, choose "topology" folder
        # if os.environ['CLUSTER'] == 1, choose "topology_kmeans" folder
        if os.environ['CLUSTER'] == '0':
            self.topology = self.get_topology(os.environ['NODES'], "topology")
        else:
            self.topology = self.get_topology(os.environ['NODES'], "topology_kmeans")

        # Find neighbors based on the topology (with latency)
        # but not from the real network
        self.neighbor_pods = self._find_neighbors(self.pod_name)
        print(f"{self.pod_name}({self.host}) neighbors: {self.neighbor_pods}", flush=True)

        self.received_messages = set()

        self.gossip_initiated = False
        self.initial_gossip_timestamp = None

    def get_topology(self, total_replicas, topology_folder, statefulset_name="gossip-statefulset",  namespace="default"):
        """
        Retrieves the number of replicas for the specified StatefulSet using kubectl
        and finds the corresponding topology file in the 'topology' subfolder
        within the current working directory.
        """



        # Get the current working directory
        current_directory = os.getcwd()

        # Construct the full path to the topology folder
        topology_dir = os.path.join(current_directory, topology_folder)

        # Find the corresponding topology file
        topology_file = None
        for topology_filename in os.listdir(topology_dir):
            if topology_folder == 'topology':
                if topology_filename.startswith(f'nodes{total_replicas}_'):
                    topology_file = topology_filename
                    break
            else:
                if topology_filename.startswith(f'kmeans_nodes{total_replicas}_'):
                    topology_file = topology_filename
                    break
        # print(f"topology_dir: {topology_dir}", flush=True)
        # print(f"topology_folder : {topology_folder }", flush=True)
        # print(f"topology_file: {topology_file}", flush=True)

        if topology_file:
            with open(os.path.join(topology_dir, topology_file), 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"No topology file found for {total_replicas} nodes.")

    def get_pod_ip(self, pod_name, namespace="default"):
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip

    # Receiving message from other nodes
    # and distribute it to others
    def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id
        received_timestamp = time.time_ns()

        # Get latency info of each gossip
        # 0.00ms for self initiated message
        # Depends on the latency of the current neighbor latency info
        received_latency = request.latency_ms

        # Check for message initiation and set the initial timestamp
        if sender_id == self.pod_name and not self.gossip_initiated:
            self.gossip_initiated = True
            self.initial_gossip_timestamp = received_timestamp
            log_message = (f"Gossip initiated by {self.pod_name}({self.host}) at "
                           f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(received_timestamp / 1e9))}"
                           f"with no latency: {received_latency} ms")
            self._log_event(message, sender_id, received_timestamp, None,
                            received_latency, 'initiate', log_message)
            self.gossip_initiated = False  # For multiple tests, need to reset gossip initialization

        # Check for duplicate messages
        elif message in self.received_messages:
            log_message = (f"{self.pod_name}({self.host}) ignoring duplicate message: '{message}' "
                           f"from {sender_id} with latency={received_latency}ms")
            self._log_event(message, sender_id, received_timestamp, None,received_latency, 'duplicate', log_message)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by {self.pod_name}({self.host})")

        # Send to message neighbor (that is  not receiving the message yet)
        else:
            self.received_messages.add(message)
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            log_message = (f"{self.pod_name}({self.host}) received: '{message}' from {sender_id}"
                           f" in {propagation_time:.2f} ms with latency of: {received_latency} ms")
            self._log_event(message, sender_id, received_timestamp, propagation_time,received_latency, 'received', log_message)

        # Gossip to neighbors (only if the message is new)
        self.gossip_message(message, sender_id)
        return gossip_pb2.Acknowledgment(details=f"{self.pod_name}({self.host}) processed message: '{message}'")

    # This function objective is to send message to all neighbor nodes.
    # In real environment, suppose we should get latency from
    # networking tools such as iperf. But it will be included in
    # future work. For the sake of this simulation, we will get
    # neighbor latency based by providing delay using the pre-defined
    # latency value. Formula: time.sleep(latency_ms/1000)
    def gossip_message(self, message, sender_id):

        # Get the neighbor and its latency
        for neighbor_pod_name, neighbor_latency in self.neighbor_pods:
            if neighbor_pod_name != sender_id:
                neighbor_ip = self.get_pod_ip(neighbor_pod_name)
                target = f"{neighbor_ip}:5050"

                # Record the send timestamp
                send_timestamp = time.time_ns()

                # Introduce latency here
                time.sleep(int(neighbor_latency) / 1000)

                with grpc.insecure_channel(target) as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(
                            message=message,
                            sender_id=self.pod_name,
                            timestamp=send_timestamp,
                            latency_ms=neighbor_latency  # neighbor latency in miliseconds
                        ))
                        print(
                            f"{self.pod_name}({self.host}) forwarded message: '{message}' to {neighbor_pod_name} ({neighbor_ip}) "
                            f"with latency {neighbor_latency} ms",
                            flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message: '{message}' to {neighbor_pod_name}: {e}", flush=True)


    def _find_neighbors(self, node_id):
        """
        Identifies the neighbors of the given node based on the topology,
        including the latency of the connection.
        """

        """
        Check whether the latency is random or fixed for all
        Random is determined by the predetermined latency_ms value
        (from helm values). If latency_ms==0, it is
        random latency option (from topology info),
        while fix is otherwise (latency_ms>0)
        """
        if (int(os.environ['LATENCY']) > 0):
            latency_ms = int(os.environ['LATENCY'])
        else:
            latency_ms = 0

        neighbors = []
        for edge in self.topology['edges']:
            if edge['source'] == node_id:
                if latency_ms > 0:
                    neighbors.append((edge['target'], latency_ms))  # Add neighbor and latency as a tuple (from values)
                else:
                    neighbors.append((edge['target'], edge['latency']))  # Add neighbor and latency as a tuple (from topology)
            elif edge['target'] == node_id:
                if latency_ms > 0:
                    neighbors.append((edge['source'], latency_ms))  # Add neighbor and latency as a tuple (from values)
                else:
                    neighbors.append((edge['source'], edge['latency']))  # Add neighbor and latency as a tuple

        return neighbors


    def _log_event(self, message, sender_id, received_timestamp, propagation_time, latency_ms, event_type, log_message):
        """Logs the gossip event as structured JSON data."""
        event_data = {
            'message': message,
            'sender_id': sender_id,
            'receiver_id': self.pod_name,
            'received_timestamp': received_timestamp,
            'propagation_time': propagation_time,
            'latency_ms': latency_ms,
            'event_type': event_type,
            'detail': log_message
        }

        # Log the JSON data using the logging module (for potential future use)
        logging.info(json.dumps(event_data))

        # Print both the log message and the JSON data to the console
        # print(log_message, flush=True)
        print(json.dumps(event_data), flush=True)

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.pod_name}({self.host}) listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()


def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()


if __name__ == '__main__':
    run_server()
