# initiate_gossip.py
import asyncio
import grpc
import gossip_pb2
import gossip_pb2_grpc

async def send_message(target_port, message):
    async with grpc.aio.insecure_channel(f'localhost:{target_port}') as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        await stub.SendMessage(gossip_pb2.GossipMessage(message=message))
        print(f"Message sent to Node at port {target_port}")

if __name__ == '__main__':
    target_port = input("Enter target node port: ")
    message = input("Enter message to send: ")
    asyncio.run(send_message(target_port, message))
