import grpc
import argparse
import time
import socket
from your_service_pb2 import GossipRequest
from your_service_pb2_grpc import GossipStub


def send_message(message, target_node):
    """Sends a gossip message to the specified target node."""

    target = f"{target_node}.bcgossip-svc:50051"

    with grpc.insecure_channel(target) as channel:
        stub = GossipStub(channel)
        print(f"Sending gossip message to {target_node}: '{message}'", flush=True)

        try:
            response = stub.Gossip(
                GossipRequest(sender=socket.gethostname(), timestamp=time.time_ns(), payload=message))
            print(f"Received acknowledgment: Node {response.sender} at {response.timestamp}", flush=True)
        except grpc.RpcError as e:
            print(f"Error sending message to {target_node}: {e}", flush=True)


def initiate_gossip(message):
    """Initiates the gossip protocol by sending a message to self and then to neighbors."""

    my_node_id = socket.gethostname()

    # 1. Send to self
    send_message(message, my_node_id)

    # 2. Load topology and send to neighbors
    with open('/app/config/network_topology.json', 'r') as f:
        topology = json.load(f)

    neighbors = [link['target'] for link in topology['links'] if link['source'] == my_node_id] + \
                [link['source'] for link in topology['links'] if link['target'] == my_node_id]

    for neighbor in neighbors:
        send_message(message, neighbor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initiate gossip protocol.")
    parser.add_argument('--message', required=True, help="Message to send")
    args = parser.parse_args()

    initiate_gossip(args.message)
