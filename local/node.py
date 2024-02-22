# node.py
import asyncio
import grpc
import sys
from google.protobuf import empty_pb2
import gossip_pb2
import gossip_pb2_grpc

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, node_id, port, peers):
        self.node_id = node_id
        self.port = port
        self.peers = peers
        self.received_messages = set()

    async def SendMessage(self, request, context):
        message = request.message
        print(f"Node {self.node_id} received message: '{message}'")
        if message not in self.received_messages:
            self.received_messages.add(message)
            await self.gossip_message(message)
        return empty_pb2.Empty()

    async def gossip_message(self, message):
        for peer in self.peers:
            async with grpc.aio.insecure_channel(peer) as channel:
                try:
                    stub = gossip_pb2_grpc.GossipServiceStub(channel)
                    await stub.SendMessage(gossip_pb2.GossipMessage(message=message))
                    print(f"Node {self.node_id} forwarded message to {peer}")
                except grpc.aio.AioRpcError as e:
                    print(f"Failed to send message to {peer}: {e}")

    async def start_server(self):
        server = grpc.aio.server()
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        # server.add_insecure_port(f'127.0.0.1:{self.port}')
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"Node {self.node_id} listening on port {self.port}")
        await server.start()
        await server.wait_for_termination()

async def run_server(node_id, port, peers):
    node = Node(node_id, port, peers.split(","))
    await node.start_server()

if __name__ == '__main__':
    node_id, port, peers = sys.argv[1:4]
    asyncio.run(run_server(node_id, port, peers))
