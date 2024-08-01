import grpc
from concurrent import futures
import time
from bcgossip_pb2 import *
from bcgossip_pb2_grpc import *

class GossipServer(GossipServicer):
    def Gossip(self, request, context):
        print(f"Received message: '{request.payload}' from {request.sender} "
              f"at {request.timestamp}", flush=True)
        return GossipResponse(sender="Server", timestamp=time.time_ns(), payload=request.payload)  # Echo back the message

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_GossipServicer_to_server(GossipServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started, listening on 50051", flush=True)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
