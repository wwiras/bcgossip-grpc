from kubernetes import client, config
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = '5050'
        self.service_name = service_name
        self.susceptible_nodes = []
        self.received_messages = set()

    def get_neighbours(self):
        self.susceptible_nodes = []
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            if i.metadata.labels:
                for k, v in i.metadata.labels.items():
                    if k == 'run' and v == self.service_name and self.host != i.status.pod_ip:
                        self.susceptible_nodes.append(i.status.pod_ip)

    def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id
        if message not in self.received_messages:
            self.received_messages.add(message)
            if sender_id == "initiate":
                # This checks if the message is from initiate.py and logs accordingly
                print(f"Initiating gossip from {self.host} for message: '{message}'", flush=True)
            else:
                print(f"Received message: '{message}' from {sender_id}", flush=True)
            self.gossip_message(message, sender_id)
            return gossip_pb2.Acknowledgment(details=f"{self.host} received: '{message}'")
        else:
            return gossip_pb2.Acknowledgment(details=f"{self.host} ignored duplicate: '{message}'")

    def gossip_message(self, message, sender_id):
        self.get_neighbours()
        for peer_ip in self.susceptible_nodes:
            if peer_ip != self.host:  # Avoid sending back to itself
                with grpc.insecure_channel(f"{peer_ip}:5050") as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=self.host))
                    except grpc.RpcError as e:
                        print(f"Failed to send message to {peer_ip}: {e}", flush=True)

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        server.start()
        server.wait_for_termination()

def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()

if __name__ == '__main__':
    run_server()
