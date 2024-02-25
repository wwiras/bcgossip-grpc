import grpc
import argparse
import gossip_pb2
import gossip_pb2_grpc
import socket

def send_message_to_self(message):
    # Obtain the host's own IP to use as both the sender and the target
    host_ip = socket.gethostbyname(socket.gethostname())
    target = f"{host_ip}:5050"

    with grpc.insecure_channel(target) as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        response = stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=host_ip))
        print(f"Received acknowledgment: {response.details}", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initiate gossip protocol by sending a message to self.")
    parser.add_argument('--message', required=True, help="Message to send to self")
    args = parser.parse_args()
    send_message_to_self(args.message)
