import grpc
from concurrent import futures
import time, socket
from bcgossip_pb2 import *
from bcgossip_pb2_grpc import *

class GossipServer(GossipServiceServicer):
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        print(f"self.host={self.host}",flush=True)
        self.received_messages = set()  # Keep track of received messages

    def SendMessage(self, request, context):
        message = request.message.strip()
        sender_ip = request.sender_id
        timestamp = request.timestamp

        # Calculate propagation time
        propagation_time = time.time_ns() - timestamp

        # Check for duplicates
        if message in self.received_messages:
            print(f"{self.host} ignored duplicate: '{message}' from {sender_ip} (propagation time: {propagation_time} ns)", flush=True)
            return Acknowledgment(details=f"{self.host} ignored duplicate: '{message}'")
        else:
            self.received_messages.add(message)
            print(f"{self.host} received: '{message}' from {sender_ip} (propagation time: {propagation_time} ns)", flush=True)
            return Acknowledgment(details=f"{self.host} received: '{message}'")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_GossipServiceServicer_to_server(GossipServer(), server)
    server.add_insecure_port(f'[::]:50051')
    server.start()
    print(f"Server started, listening on 50051", flush=True)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
