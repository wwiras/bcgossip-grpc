
import grpc
import json
import random
import time
import os
from concurrent import futures
from bcgossip_pb2 import *
from bcgossip_pb2_grpc import *


class GossipServer(GossipServicer):
    def __init__(self):
        self.pod_name = os.environ['NODE_NAME']  # Get the pod's name

        with open('/app/config/network_topology.json', 'r') as f:
            self.topology = json.load(f)
        self.neighbors = self._find_neighbors(self.pod_name)
        print(f"Neighbors={self.neighbors}", flush=True)
        self.seen_messages = set()
        self.blockchain = []  # A simple list to represent the blockchain

    def _find_neighbors(self, node_id):
        """Identifies the neighbors of the given node based on the topology."""
        neighbors = []
        for link in self.topology['links']:
            if link['source'] == node_id:
                neighbors.append(link['target'])
            elif link['target'] == node_id:
                neighbors.append(link['source'])
        return neighbors

    def validate_message(self, message):
        """Simulates basic message validation (replace with your actual logic)."""
        # In a real blockchain, this would involve complex validation of the message signature, content, etc.
        return True

    def add_message_to_blockchain(self, message):
        """Simulates adding the message to the blockchain (replace with your actual logic)."""
        # In a real blockchain, this would involve updating the blockchain's data structure and potentially broadcasting the new block.
        self.blockchain.append(message)
        print(f"Node {self.node_id} added message '{message.payload}' to blockchain", flush=True)

    def Gossip(self, request, context):
        """Handles incoming gossip messages and forwards them to neighbors."""
        # --- Blockchain Logic ---
        if self.validate_message(request):
            self.add_message_to_blockchain(request)

        # --- Measure Propagation Time ---
        propagation_time = time.time_ns() - request.timestamp

        # --- Log Propagation Time (replace with your logging mechanism) ---
        print(f"Node {self.node_id} received message '{request.payload}' "
              f"(propagation time: {propagation_time} ns)", flush=True)

        # Check for duplicates
        message_key = (request.sender, request.payload)
        if message_key in self.seen_messages:
            print(f"Duplicate message detected from {request.sender}. Ignoring.", flush=True)
            return GossipResponse(sender=self.node_id, timestamp=time.time_ns(), payload=request.payload)

        self.seen_messages.add(message_key)

        # Randomly select a neighbor for forwarding (without weights)
        neighbors_to_forward = [n for n in self.neighbors if n != request.sender]
        if neighbors_to_forward:
            neighbor = random.choice(neighbors_to_forward)

            # Forward message
            with grpc.insecure_channel(f'{neighbor}:50051') as channel:
                stub = GossipStub(channel)
                response = stub.Gossip(request)
                print(f"Forwarded message to {neighbor} at {response.timestamp}", flush=True)

        return GossipResponse(sender=self.node_id, timestamp=time.time_ns(), payload=request.payload)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_GossipServicer_to_server(GossipServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Gossip server started on port 50051", flush=True)
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
