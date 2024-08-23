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

# Import for gRPC reflection
from grpc_reflection.v1alpha import reflection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):

        self.pod_name = socket.gethostname()
        self.host = socket.gethostbyname(self.pod_name)
        self.port = '5050'
        self.service_name = service_name

        # Load the topology from the "topology" folder
        self.topology = self.get_topology(10, "topology")

        # Find neighbors based on the topology (without measuring latency yet)
        self.neighbor_pod_names = self._find_neighbors(self.pod_name)
        print(f"{self.pod_name}({self.host}) neighbors: {self.neighbor_pod_names}", flush=True)

        self.received_messages = set()

        self.gossip_initiated = False
        self.initial_gossip_timestamp = None

    def get_topology(self, total_replicas, topology_folder, statefulset_name="gossip-statefulset",  namespace="default"):
        """
        Retrieves the number of replicas for the specified StatefulSet using kubectl
        and finds the corresponding topology file in the 'topology' subfolder
        within the current working directory.
        """

        # Get the StatefulSet replica count using kubectl
        # command = f"kubectl get statefulset {statefulset_name} -n {namespace} -o jsonpath='{{.spec.replicas}}'"
        #         # try:
        #         #     total_replicas = int(subprocess.check_output(command, shell=True).decode('utf-8').strip())
        #         # except subprocess.CalledProcessError as e:
        #         #     raise RuntimeError(f"Error getting StatefulSet replicas using kubectl: {e}")


        # Get the current working directory
        current_directory = os.getcwd()

        # Construct the full path to the topology folder
        topology_folder = os.path.join(current_directory, topology_folder)

        # Find the corresponding topology file
        topology_file = None
        for topology_filename in os.listdir(topology_folder):
            if topology_filename.startswith(f'nt_nodes{total_replicas}_'):
                topology_file = topology_filename
                break

        if topology_file:
            with open(os.path.join(topology_folder, topology_file), 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"No topology file found for {total_replicas} nodes.")

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

                # Get bandwidth for this specific connection from topology
                bandwidth_kbps = next((link['bandwidth'] * 1000 / 8
                                       for link in self.topology['links']
                                       if (link['source'] == self.pod_name and link['target'] == neighbor_pod_name) or
                                       (link['target'] == self.pod_name and link['source'] == neighbor_pod_name)),
                                      None)  # Default to None if no bandwidth found

                try:
                    # Construct trickle command with bandwidth limit (if available)
                    trickle_command = ["trickle"]
                    if bandwidth_kbps:
                        trickle_command.extend(["-s", "-d", str(bandwidth_kbps), "-u", str(bandwidth_kbps)])

                    # Prepare the input data for grpcurl
                    input_data = {
                        "message": message,
                        "sender_id": self.pod_name,
                        "timestamp": received_timestamp
                    }

                    # Construct the grpcurl command
                    grpcurl_command = [
                        "grpcurl",
                        "--plaintext",
                        "-d", json.dumps(input_data),
                        target,
                        "gossip.GossipService/SendMessage"
                    ]

                    # Combine trickle and grpcurl commands
                    full_command = trickle_command + grpcurl_command

                    # Execute the combined command and capture output
                    result = subprocess.check_output(full_command)

                    # Parse the JSON response (if needed)
                    # response = json.loads(result)

                    # Print the response for debugging
                    # print(f"Response from {neighbor_pod_name}: {response}", flush=True)

                    print(
                        f"{self.pod_name}({self.host}) forwarded message: '{message}' to {neighbor_pod_name} ({neighbor_ip})",
                        flush=True)

                except subprocess.CalledProcessError as e:
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

        # Enable gRPC reflection on the server
        SERVICE_NAMES = (
            gossip_pb2.DESCRIPTOR.services_by_name['GossipService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

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

## Test sending grpcurl with trickle
#trickle -s -d 125 -u 125 grpcurl -plaintext -proto gossip.proto -d '{"message": "testgrpcurldirect", "sender_id": "gossip-statefulset-0", "timestamp": 1234567890}' 10.44.1.17:5050 gossip.GossipService/SendMessage