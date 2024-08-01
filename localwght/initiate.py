import grpc
import argparse
import time
from bcgossip_pb2 import *
from bcgossip_pb2_grpc import *

def send_message(message):
    with grpc.insecure_channel('localhost:50000') as channel:
        stub = GossipStub(channel)
        response = stub.Gossip(GossipRequest(sender="Client", timestamp=time.time_ns(), payload=message))
        print(f"Server response: {response.payload} from {response.sender} at {response.timestamp}", flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send a message to the server.")
    parser.add_argument('--message', required=True, help="Message to send")
    args = parser.parse_args()

    send_message(args.message)
