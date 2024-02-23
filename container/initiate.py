import asyncio
import grpc
import argparse
import gossip_pb2
import gossip_pb2_grpc

async def send_message(target_node, message, sender_id):
    async with grpc.aio.insecure_channel(f'{target_node}:5050') as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        await stub.SendMessage(gossip_pb2.GossipMessage(message=message, sender_id=sender_id))
        print(f"Message sent from {sender_id} to {target_node}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Initiate gossip protocol.")
    parser.add_argument('--target_node', required=True, help="Target node container name")
    parser.add_argument('--message', required=True, help="Message to send")
    parser.add_argument('--sender_id', required=True, help="Sender node ID (container name)")
    args = parser.parse_args()
    asyncio.run(send_message(args.target_node, args.message, args.sender_id))
