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

        # Set initial bandwidth limits to 2 Mbps
        self.set_bandwidth_limits(ingress_limit="2mbit", egress_limit="2mbit")

    # ... (rest of the methods: get_pod_ip, SendMessage, gossip_message, _find_neighbors remain the same) ...

    def set_bandwidth_limits(self, ingress_limit, egress_limit, interface="eth0"):
        """
        Sets ingress and egress bandwidth limits using tc.
        """
        try:
            # Set ingress limit
            subprocess.run([
                'tc', 'qdisc', 'add', 'dev', interface, 'root', 'handle', '1:', 'ingress'
            ], check=True)
            subprocess.run([
                'tc', 'filter', 'add', 'dev', interface, 'parent', '1:', 'protocol', 'ip', 'prio', '1', 'u32',
                'match', 'ip', 'dst', '0.0.0.0/0', 'police', 'rate', ingress_limit, 'burst', '10k', 'drop', 'flowid', ':1'
            ], check=True)

            # Set egress limit
            subprocess.run([
                'tc', 'qdisc', 'add', 'dev', interface, 'root', 'handle', '1:', 'htb', 'default', '1'
            ], check=True)
            subprocess.run([
                'tc', 'class', 'add', 'dev', interface, 'parent', '1:', 'classid', '1:1', 'htb',
                'rate', egress_limit, 'ceil', egress_limit
            ], check=True)

            print(f"Bandwidth limits set on {interface}: ingress={ingress_limit}, egress={egress_limit}", flush=True)

        except subprocess.CalledProcessError as e:
            logging.error(f"Error setting bandwidth limits: {e}")

    def _log_event(self, message, sender_id, received_timestamp, propagation_time, event_type, log_message):
        """Logs the gossip event as structured JSON data."""
        # ... (same as before)

    def start_server(self):
        # ... (same as before)


def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()


if __name__ == '__main__':
    run_server()
