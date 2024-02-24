import os
import json
# from dapr.ext.grpc import App, InvokeServiceRequest, InvokeServiceResponse
from dapr.clients import DaprClient
from dapr.ext.grpc import InvokeMethodRequest, InvokeMethodResponse, App
app = App()

current_node = os.getenv('NODE_NAME')
neighbors = os.getenv('NEIGHBORS').split(',')


@app.method(name='my-method')
# def my_method(request: InvokeServiceRequest) -> InvokeServiceResponse:
def my_method(request: InvokeMethodRequest) -> InvokeMethodResponse:
    print(f"Received message at {current_node}: {request.text()}", flush=True)
    message = json.loads(request.text())
    sender = message['sender']

    # Forward the message to neighbors, excluding the sender
    for neighbor in neighbors:
        if neighbor != sender:
            send_message(neighbor, message)

    # return InvokeServiceResponse(b'INVOKE_RECEIVED', "text/plain; charset=UTF-8")
    return InvokeMethodResponse(b'INVOKE_RECEIVED', "text/plain; charset=UTF-8")


def send_message(target_service, message):
    with DaprClient() as d:
        print(f"Sending message from {current_node} to {target_service}", flush=True)
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
    print(f"Node {current_node} listening on port 50051", flush=True)
    app.run(50051)

