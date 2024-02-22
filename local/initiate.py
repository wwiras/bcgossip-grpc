# initiate_gossip.py
import asyncio
import grpc
import gossip_pb2
import gossip_pb2_grpc

async def send_message(target_port, message, sender_id):
    async with grpc.aio.insecure_channel(f'localhost:{target_port}') as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        response = await stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=sender_id))
        print(f"Received acknowledgment: {response.details}")

if __name__ == '__main__':
    target_port = input("Enter target node port: ")
    message = input("Enter message to send: ")
    sender_id = input("Enter sender node ID: ")
    asyncio.run(send_message(target_port, message, sender_id))
