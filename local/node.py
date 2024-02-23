# node.py
import asyncio
import grpc
import sys
import gossip_pb2
import gossip_pb2_grpc

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, node_id, port, peers):
        self.node_id = node_id
        self.port = port
        self.peers = peers  # List of other node addresses in "host:port" format
        # print(self.peers)
        self.received_messages = set()

    async def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id
        print(f"Node {self.node_id} received message: '{message}' from Node {sender_id}")
        if message not in self.received_messages:
            self.received_messages.add(message)
            await self.gossip_message(message, sender_id)
            return gossip_pb2.Acknowledgment(details=f"Node {self.node_id} received: '{message}' from Node {sender_id}")
        else:
            return gossip_pb2.Acknowledgment(details=f"Node {self.node_id} ignored duplicate: '{message}' from Node {sender_id}")

    async def gossip_message(self, message, sender_id):
        # Exclude the sender from the list of peers to forward the message to
        peers_to_notify = [peer for peer in self.peers if peer != sender_id]
        # print(peers_to_notify)
        for peer in peers_to_notify:
            async with grpc.aio.insecure_channel(peer) as channel:
                try:
                    stub = gossip_pb2_grpc.GossipServiceStub(channel)
                    await stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=self.port))
                    print(f"Node {self.node_id} forwarded message to {peer}")
                except grpc.aio.AioRpcError as e:
                    print(f"Failed to send message to {peer}: {e}")

    async def start_server(self):
        server = grpc.aio.server()
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
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
