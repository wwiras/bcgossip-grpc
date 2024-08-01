import grpc
import argparse
import time
from bcgossip_pb2 import *
from bcgossip_pb2_grpc import *

def send_message(message, target_node):
    """Sends a gossip message to the specified target node."""

    # Construct the target address using the node's DNS name and the service name
    target = f"{target_node}.bcgossip-svc:50051"

    with grpc.insecure_channel(target) as channel:
        stub = GossipStub(channel)
        response = stub.Gossip(GossipRequest(sender=socket.gethostname(), timestamp=time.time_ns(), payload=message))
        print(f"Server response: {response.payload} from {response.sender} at {response.timestamp}", flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send a message to the server.")
    parser.add_argument('--message', required=True, help="Message to send")
    parser.add_argument('--target', required=True, help="Target node to send the message to (e.g., gossip-statefulset-0)")
    args = parser.parse_args()

    send_message(args.message, args.target)
