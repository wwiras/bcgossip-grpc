import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
from kubernetes import client, config


class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())  # Get own pod IP
        self.port = '5050'  # Corrected port number

    def SendMessage(self, request, context):
        print(f"{self.host} received: '{request.message}' from {request.sender_id}", flush=True)
        return gossip_pb2.Acknowledgment(details="Message received successfully")

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.host} listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()

def run_server():
    node = Node()
    node.start_server()

if __name__ == '__main__':
    run_server()
