import grpc
import argparse
import time
import socket
from bcgossip_pb2 import GossipRequest
from bcgossip_pb2_grpc import GossipStub

def send_message_to_self(message):
    """Initiates the gossip protocol by sending a message to self."""
    node_id = socket.gethostname()  # Use the pod's DNS name directly
    target = f"{node_id}.bcgossip-svc:50051"  # Using the headless service name

    with grpc.insecure_channel(target) as channel:
        stub = GossipStub(channel)
        print(f"Initiating gossip from {node_id} with message: '{message}'", flush=True)
        response = stub.Gossip(GossipRequest(sender=node_id, timestamp=time.time_ns(), payload=message))
        print(f"Received acknowledgment: Node {response.sender} at {response.timestamp}", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initiate gossip protocol by sending a message to self.")
    parser.add_argument('--message', required=True, help="Message to send to self")
    args = parser.parse_args()
    send_message_to_self(args.message)
