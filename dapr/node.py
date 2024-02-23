import os
import json
from dapr.ext.grpc import App, InvokeServiceRequest, InvokeServiceResponse
from dapr.clients import DaprClient

app = App()

current_node = os.getenv('NODE_NAME')
neighbors = os.getenv('NEIGHBORS').split(',')


@app.method(name='my-method')
def my_method(request: InvokeServiceRequest) -> InvokeServiceResponse:
    print(f"Received message at {current_node}: {request.text()}", flush=True)
    message = json.loads(request.text())
    sender = message['sender']

    # Forward the message to neighbors, excluding the sender
    for neighbor in neighbors:
        if neighbor != sender:
            send_message(neighbor, message)

    return InvokeServiceResponse(b'INVOKE_RECEIVED', "text/plain; charset=UTF-8")


def send_message(target_service, message):
    with DaprClient() as d:
        print(f"Sending message from {current_node} to {target_service}", flush=True)
        d.invoke_service(
            target_service,
            'my-method',
            data=json.dumps(message),
        )


if __name__ == "__main__":
    app.run(50051)
