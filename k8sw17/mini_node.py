import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
import json
import time
import logging
import argparse  # Import argparse for command-line arguments

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(message)s')

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, cluster, model, total_nodes):

        self.pod_name = socket.gethostname()
        self.pod_ip = socket.gethostbyname(self.pod_name)
        self.port = '5050'
        self.model = model
        self.total_nodes = total_nodes
        self.cluster = cluster

        # Determine the topology folder based on cluster type
        topology_folder = "topology" if self.cluster == '0' else "topology_kmeans"

        # Get topology based on model, cluster, and total number of nodes
        self.topology = self.get_topology(topology_folder)

        # Find neighbors based on the topology (with latency)
        self.neighbor_hosts = self._find_neighbors(self.pod_name)
        print(f"{self.pod_name}({self.pod_ip}) neighbors: {self.neighbor_hosts}", flush=True)

        self.received_messages = set()
        self.gossip_initiated = False
        self.initial_gossip_timestamp = None

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
            log_message = (f"Gossip initiated by {self.pod_name}({self.pod_ip}) at "
                           f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(received_timestamp / 1e9))}"
                           f"with no latency: {received_latency} ms")
            self._log_event(message, sender_id, received_timestamp, None,
                            received_latency, 'initiate', log_message)
            self.gossip_initiated = False  # For multiple tests, need to reset gossip initialization

        # Check for duplicate messages
        elif message in self.received_messages:
            log_message = (f"{self.pod_name}({self.pod_ip}) ignoring duplicate message: '{message}' "
                           f"from {sender_id} with latency={received_latency}ms")
            self._log_event(message, sender_id, received_timestamp, None, received_latency, 'duplicate',
                            log_message)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by {self.pod_name}({self.pod_ip})")

        # Send to message neighbor (that is  not receiving the message yet)
        else:
            self.received_messages.add(message)
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            log_message = (f"{self.pod_name}({self.pod_ip}) received: '{message}' from {sender_id}"
                           f" in {propagation_time:.2f} ms with latency of: {received_latency} ms")
            self._log_event(message, sender_id, received_timestamp, propagation_time, received_latency, 'received',
                            log_message)

        # Gossip to neighbors (only if the message is new)
        self.gossip_message(message, sender_id)
        return gossip_pb2.Acknowledgment(details=f"{self.pod_name}({self.pod_ip}) processed message: '{message}'")

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
                # neighbor_ip = self.get_pod_ip(neighbor_pod_name)
                neighbor_ip = socket.gethostbyname(neighbor_pod_name)
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
                        # print(
                        #     f"{self.pod_name}({self.pod_ip}) forwarded message: '{message}' to {neighbor_pod_name} ({neighbor_ip}) "
                        #     f"with latency {neighbor_latency} ms",
                        #     flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message: '{message}' to {neighbor_pod_name}: {e}", flush=True)

    def get_topology(self,topology_folder):
        """
        Retrieves the topology file from the specified folder based on the number of nodes and model.
        """
        current_directory = os.getcwd()
        topology_dir = os.path.join(current_directory, topology_folder)

        # Construct the search string based on the cluster and model
        search_str = f'nodes{self.total_nodes}_' if self.cluster == '0' else f'kmeans_nodes{self.total_nodes}_'

        # Find the corresponding topology file
        topology_file = None
        for topology_filename in os.listdir(topology_dir):
            if topology_filename.startswith(search_str) and self.model in topology_filename:
                topology_file = topology_filename
                break

        if topology_file:
            with open(os.path.join(topology_dir, topology_file), 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"No topology file found for {self.total_nodes} nodes and model {self.model}.")

    def _find_neighbors(self, node_id):
        """
        Identifies the neighbors of the given node based on the topology.
        """
        # latency_option = os.environ.get('LATENCY_OPTION', 'weight')  # Default to 'weight'
        latency_option = 'weight'
        neighbors = []
        for edge in self.topology['edges']:
            if edge['source'] == node_id:
                neighbors.append((edge['target'], edge[latency_option]))  # Add neighbor and latency
            elif edge['target'] == node_id:
                neighbors.append((edge['source'], edge[latency_option]))  # Add neighbor and latency
        return neighbors

    def _log_event(self, message, sender_id, received_timestamp, propagation_time, latency_ms, event_type, log_message):
        """
        Logs the gossip event as structured JSON data.
        """
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
        print(json.dumps(event_data), flush=True)

    def start_server(self):
        """
        Starts the gRPC server for the node.
        """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.pod_name}({self.pod_ip}) listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()

    def run_server(cluster, model, total_nodes):
        """
        Initializes and runs the node server.
        """
        node = Node(cluster, model, total_nodes)
        node.start_server()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a gossip node.")
    parser.add_argument('--cluster', required=True, choices=['0', '1'], help="Cluster type: 0 for non-clustered, 1 for k-means clustered")
    parser.add_argument('--model', required=True, choices=['BA', 'ER'], help="Topology model: BA or ER")
    parser.add_argument('--nodes', required=True, type=int, help="Total number of nodes in the topology")
    args = parser.parse_args()

    run_server(args.cluster, args.model, args.nodes)