from kubernetes import client, config
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):
        self.podname = socket.gethostname()
        self.host = socket.gethostbyname(self.podname)  # Get own pod IP
        self.port = '5050'
        self.service_name = service_name
        # Hardcoded neighbor pod names (excluding self)
        all_pod_names = [f"gossip-statefulset-{i}" for i in range(4)]  # Assuming 2 replicas
        self.neighbor_pod_names = [n for n in all_pod_names if n != self.podname]
        self.received_messages = set()  # Use a set to track received messages

    def get_pod_ip(self, pod_name, namespace="default"):
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip

    def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id

        # Check for message initiation (using pod name for comparison)
        if sender_id == self.podname:
            print(f"Message '{message}' initiated by {self.podname}({self.host})", flush=True)
            self.received_messages.add(message)  # Add the message to received_messages

        # Check for duplicate messages
        elif message in self.received_messages:
            print(f"{self.podname}({self.host}) ignoring duplicate message: '{message}' from {sender_id}", flush=True)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by {self.podname}({self.host})")
        else:
            self.received_messages.add(message)
            print(f"{self.podname}({self.host}) received: '{message}' from {sender_id}", flush=True)

        # Gossip to neighbors (only if the message is new)
        self.gossip_message(message, sender_id)
        return gossip_pb2.Acknowledgment(details=f"{self.podname}({self.host}) processed message: '{message}'")

    def gossip_message(self, message, sender_id):
        for neighbor_pod_name in self.neighbor_pod_names:
            if neighbor_pod_name != sender_id:
                neighbor_ip = self.get_pod_ip(neighbor_pod_name)
                target = f"{neighbor_ip}:5050"
                with grpc.insecure_channel(target) as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=self.podname))
                        print(f"{self.podname}({self.host}) forwarded message to {neighbor_pod_name} ({neighbor_ip})", flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message to {neighbor_pod_name}: {e}", flush=True)

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.podname}({self.host}) listening on port {self.port}", flush=True)  # Changed here
        server.start()
        server.wait_for_termination()

def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')  # Make sure this matches your Kubernetes service labels
    node = Node(service_name)
    node.start_server()

if __name__ == '__main__':
    run_server()
