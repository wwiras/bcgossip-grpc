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
import netifaces # For running ping or other latency measurement tools

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

        # Set initial bandwidth limits to 2 Mbps
        self.set_bandwidth_limits(ingress_limit="1mbit", egress_limit="1mbit")

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
            log_message = f"{self.pod_name}({self.host}) received: '{message}' from {sender_id} in {propagation_time:.2f} ms"
            self._log_event(message, sender_id, received_timestamp, propagation_time, 'received', log_message)

        # Gossip to neighbors (only if the message is new)
        self.gossip_message(message, sender_id, received_timestamp)
        return gossip_pb2.Acknowledgment(details=f"{self.pod_name}({self.host}) processed message: '{message}'")

    def gossip_message(self, message, sender_id, received_timestamp):
        for neighbor_pod_name in self.neighbor_pod_names:
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

    def set_bandwidth_limits(self, ingress_limit, egress_limit):
        """
        Sets ingress and egress bandwidth limits using tc, dynamically determining the interface.
        """
        try:
            # Get the default network interface
            default_gateway = netifaces.gateways()['default'][netifaces.AF_INET][1]  # Assuming IPv4
            print(f"default_gateway = {default_gateway}", flush=True)
            interface = netifaces.ifaddresses(default_gateway)[netifaces.AF_INET][0]['addr']
            print(f"interface = {interface}", flush=True)

            # Set ingress limit
            subprocess.run([
                'tc', 'qdisc', 'add', 'dev', interface, 'root', 'handle', '1:', 'ingress'
            ], check=True)
            subprocess.run([
                'tc', 'filter', 'add', 'dev', interface, 'parent', '1:', 'protocol', 'ip', 'prio', '1', 'u32',
                'match', 'ip', 'dst', '0.0.0.0/0', 'police', 'rate', ingress_limit, 'burst', '10k', 'drop', 'flowid',
                ':1'
            ], check=True)

            # Set egress limit
            subprocess.run([
                'tc', 'qdisc', 'add', 'dev', interface, 'root', 'handle', '1:', 'htb', 'default', '1'
            ], check=True)
            subprocess.run([
                'tc', 'class', 'add', 'dev', interface, 'parent', '1:', 'classid', '1:1', 'htb',
                'rate',
            egress_limit, 'ceil', egress_limit
            ], check = True)

            print(f"Bandwidth limits set on {interface}: ingress={ingress_limit}, egress={egress_limit}", flush=True)

        except subprocess.CalledProcessError as e:
            logging.error(f"Error setting bandwidth limits: {e}")
            print(f"Error setting bandwidth limits: {e}", flush=True)
        except KeyError:
            logging.error("Could not determine the default network interface.")
            print(f"Could not determine the default network interface.", flush=True)

    def _log_event(self, message, sender_id, received_timestamp, propagation_time, event_type, log_message):
        """Logs the gossip event as structured JSON data."""
        event_data = {
            'message': message,
            'sender_id': sender_id,
            'receiver_id': self.pod_name,
            'received_timestamp': received_timestamp,
            'propagation_time': propagation_time,
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
