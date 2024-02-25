import grpc
import argparse
import gossip_pb2
import gossip_pb2_grpc
import socket


def send_message_to_self(message):
    host_ip = socket.gethostbyname(socket.gethostname())
    target = f"{host_ip}:5050"

    # Here, no need for an origin_indicator in the message itself
    with grpc.insecure_channel(target) as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        # Directly use the message as provided by the user
        response = stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id="initiate"))
        print(f"Sent message. Received acknowledgment: {response.details}", flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initiate gossip protocol by sending a message to self.")
    parser.add_argument('--message', required=True, help="Message to send to self")
    args = parser.parse_args()
    send_message_to_self(args.message)
