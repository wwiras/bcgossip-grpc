import grpc
import argparse
import time  # Import time for timestamp
import socket

from bcgossip_pb2 import GossipMessage
from bcgossip_pb2_grpc import GossipServiceStub

def send_message_to_self(message):
    """Initiates the gossip protocol by sending a message to self."""

    # Obtain the host's own IP to use as both the sender and the target
    host_ip = socket.gethostbyname(socket.gethostname())
    target = f"{host_ip}:50051"  # Use the correct gRPC port (50051)

    with grpc.insecure_channel(target) as channel:
        stub = GossipServiceStub(channel)
        print(f"Initiating gossip from {host_ip}", flush=True)

        # Construct the GossipMessage with timestamp
        response = stub.SendMessage(GossipMessage(message=message, sender_id=host_ip, timestamp=time.time_ns()))

        print(f"Received acknowledgment: {response.details}", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initiate gossip protocol by sending a message to self.")
    parser.add_argument('--message', required=True, help="Message to send to self")
    args = parser.parse_args()
    send_message_to_self(args.message)
