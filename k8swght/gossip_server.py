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
        self.node_id = os.environ['NODE_NAME']
        print(f"({self.node_id})", flush = True)
        with open('/app/config/network_topology.json', 'r') as f:
            self.topology = json.load(f)
        print(f"({self.topology})", flush=True)
        self.neighbors = self._find_neighbors(self.node_id)
        print(f"({self.neighbors})", flush=True)
        self.seen_messages = set()
        self.blockchain = []

    def _find_neighbors(self, node_id):
        """Identifies the neighbors of the given node based on the topology."""
        neighbors = []
        for link in self.topology['links']:
            # print(f"link={link}", flush=True)
            if link['source'] == node_id:
                # print(f"link['source']={link['source']}", flush=True)
                neighbors.append(link['target'])
            elif link['target'] == node_id:
                # print(f"link['target']={link['target']}", flush=True)
                neighbors.append(link['source'])
        return neighbors

    def validate_message(self, message):
        """Simulates basic message validation (replace with your actual logic)."""
        return True

    def add_message_to_blockchain(self, message):
        """Simulates adding the message to the blockchain (replace with your actual logic)."""
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
        neighbor = random.choice(self.neighbors)

        # Forward message (ensure not to send back to sender)
        if neighbor != request.sender:
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
