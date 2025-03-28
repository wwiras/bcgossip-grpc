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
        # List to keep track of IPs of neighboring nodes
        self.susceptible_nodes = []
        # Set to keep track of messages that have been received to prevent loops
        self.received_message = ""
        self.gossip_initiated = False

    def get_neighbours(self):
        # Clear the existing list to refresh it
        self.susceptible_nodes = []
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            if i.metadata.labels:
                for k, v in i.metadata.labels.items():
                    if k == 'run' and v == self.service_name:
                        if self.host == i.status.pod_ip:
                            continue  # Skip own IP
                        else:
                            self.susceptible_nodes.append(i.status.pod_ip)

    def SendMessage(self, request, context):
        message = str(request.message).strip()  # Ensure message is a plain, trimmed string
        sender_ip = request.sender_id

        # For initiating acknowledgment only
        if sender_ip == self.host and not self.gossip_initiated:
            self.gossip_initiated = True
            print(f"Message: '{message}' initiated by {self.host}...", flush=True)
            self.gossip_initiated = False  # For multiple tests, need to reset gossip initialization

        # Check whether the message is already received ot not
        # Notify whether accept it or ignore it
        elif self.received_message == message:
            print(f"{self.host} ignored duplicate: '{message}' from {sender_ip}", flush=True)
            return gossip_pb2.Acknowledgment(details=f"{self.host} ignored duplicate: '{message}'")
        else:
            self.received_message = message
            print(f"{self.host} received: '{message}' from {sender_ip}", flush=True)
            # Start gossip only when the node is the gossip initiator itself
            # therefore, only one iteration is required
            # if (sender_ip == self.host):

        self.gossip_message(message, sender_ip)
        return gossip_pb2.Acknowledgment(details=f"{self.host} received: '{message}'")

    def gossip_message(self, message, sender_ip):
        # Refresh list of neighbors before gossiping to capture any changes
        self.get_neighbours()
        for peer_ip in self.susceptible_nodes:
            # Exclude the sender from the list of nodes to forward the message to
            if peer_ip != sender_ip:
                with grpc.insecure_channel(f"{peer_ip}:5050") as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=self.host))
                        print(f"{self.host} forwarded message to {peer_ip}", flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message to {peer_ip}: {e}", flush=True)

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.host} listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()

def run_server():
    # service_name = os.getenv('SERVICE_NAME', 'bcgossip')  # Make sure this matches your Kubernetes service labels
    service_name = 'bcgossip'
    node = Node(service_name)
    node.start_server()

if __name__ == '__main__':
    run_server()