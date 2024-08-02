import grpc
import argparse
import time
import socket
import gossip_pb2
import gossip_pb2_grpc

def send_message_to_self(message):
    """Sends a message to the server (pod) itself."""
    pod_name = socket.gethostname()
    target = f"{pod_name}.bcgossip-svc:5050"

    with grpc.insecure_channel(target) as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        print(f"Sending message to self ({pod_name}): '{message}'", flush=True)
        response = stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=pod_name))
        print(f"Received acknowledgment: {response.details}", flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send a message to self (the current pod).")
    parser.add_argument('--message', required=True, help="Message to send")
    args = parser.parse_args()
    send_message_to_self(args.message)
