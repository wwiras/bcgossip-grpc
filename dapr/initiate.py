import json
import os
from dapr.clients import DaprClient


def initiate_gossip(target_service, message):
    with DaprClient() as d:
        print(f"Initiating gossip to {target_service}", flush=True)
        d.invoke_method(
            target_service,
            'my-method',
            data=json.dumps(message),
        )
        # d.invoke_service(
        #     target_service,
        #     'my-method',
        #     data=json.dumps(message),
        # )


if __name__ == "__main__":
    current_node = os.getenv("NODE_NAME", "default_sender")
    target_node = input("Enter the target node's name: ")
    user_message = input("Enter the message: ")

    message_to_send = {
        'id': 1,
        'message': user_message,
        'sender': current_node,
    }

    initiate_gossip(target_node, message_to_send)
