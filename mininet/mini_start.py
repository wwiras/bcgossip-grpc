import grpc
import argparse
import time
import socket
import gossip_pb2
import gossip_pb2_grpc

def send_message_to_self(message):
    """Sends a message to the current host (itself)."""
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)  # Get the IP address of the current host
    target = f"{host_ip}:5050"
    target_latency = 0.00

    with grpc.insecure_channel(target) as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        print(f"Sending message to self ({host_name}, {host_ip}): '{message}' with latency={target_latency} ms", flush=True)
        response = stub.SendMessage(gossip_pb2.GossipMessage(
            message=message,
            sender_id=host_name,
            timestamp=time.time_ns(),
            latency_ms=target_latency
        ))
        print(f"Received acknowledgment: {response.details}", flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send a message to self (the current host).")
    parser.add_argument('--message', required=True, help="Message to send")
    args = parser.parse_args()
    send_message_to_self(args.message)