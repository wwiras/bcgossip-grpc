import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
from kubernetes import client, config


class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self):
        self.podname = socket.gethostname()
        self.host = socket.gethostbyname(self.podname)  # Get own pod IP
        self.port = '5050'
        # Get all pod names in the StatefulSet
        all_pod_names = [f"gossip-statefulset-{i}" for i in range(2)]  # Assuming 2 replicas
        # Remove the current pod's name from the neighbors
        self.neighbor_pod_names = [n for n in all_pod_names if n != socket.gethostname()]

    def SendMessage(self, request, context):
        print(f"request.sender_id={request.sender_id}", flush=True)
        print(f"self.host={self.host}", flush=True)
        print(f"self.podname={self.podname}", flush=True)
        if request.sender_id == self.podname:
            print(f"{self.podname} initiated message: '{request.message}'", flush=True)
        else:
            print(f"{self.podname} received: '{request.message}' from {request.sender_id}", flush=True)

        self.gossip_message(request.message, request.sender_id)  # Trigger gossip to neighbors
        return gossip_pb2.Acknowledgment(details="Message received successfully")

    def get_pod_ip(self, pod_name, namespace="default"):
        """Fetches the IP address of a pod in the specified namespace."""
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip

    def gossip_message(self, message, sender_id):
        """Sends the message to all neighbors except the sender."""
        for neighbor_pod_name in self.neighbor_pod_names:
            if neighbor_pod_name != sender_id:  # Filter out the original sender
                neighbor_ip = self.get_pod_ip(neighbor_pod_name)
                target = f"{neighbor_ip}:5050"
                with grpc.insecure_channel(target) as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=sender_id))
                        print(f"{self.host} forwarded message to {neighbor_pod_name} ({neighbor_ip})", flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message to {neighbor_pod_name}: {e}", flush=True)

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
