import grpc
import os
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, peers):
        self.node_id = os.getenv('NODE_ID', 'node')
        self.port = '5050'
        self.peers = peers.split(',')  # Peers are passed as a comma-separated list
        self.received_messages = set()

    def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id
        print(f"{self.node_id} received message: '{message}' from {sender_id}", flush=True)
        if message not in self.received_messages:
            self.received_messages.add(message)
            self.gossip_message(message, sender_id)
            return gossip_pb2.Acknowledgment(details=f"{self.node_id} received: '{message}'")
        else:
            return gossip_pb2.Acknowledgment(details=f"{self.node_id} ignored duplicate: '{message}'")

    def gossip_message(self, message, sender_id):
        for peer in self.peers:
            if peer != sender_id:
                with grpc.insecure_channel(f"{peer}:5050") as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=self.node_id))
                        print(f"{self.node_id} forwarded message to {peer}", flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message to {peer}: {e}", flush=True)

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.node_id} listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()

def run_server():
    peers = os.getenv('PEERS', '')  # Get peers from environment variable
    node = Node(peers)
    node.start_server()

if __name__ == '__main__':
    run_server()
