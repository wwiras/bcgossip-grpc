from kubernetes import client, config
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
import json
import time

class Node(gossip_pb2_grpc.GossipServiceServicer):

    def __init__(self, service_name):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = '5050'
        self.service_name = service_name
        # List to keep track of IPs of neighboring nodes
        self.susceptible_nodes = []
        # Set to keep track of messages that have been received to prevent loops
        self.received_messages = set()
        self.received_messages_time = time.time_ns()

    def get_neighbours(self):
        # Clear the existing list to refresh it
        self.susceptible_nodes = []
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            if i.metadata.labels:
                for k, v in i.metadata.labels.items():
                    if k == 'run' and v == self.service_name:
                        if self.host == i.status.pod_ip:
                            continue  # Skip own IP
                        else:
                            self.susceptible_nodes.append(i.status.pod_ip)

    def SendMessage(self, request, context):

        """
        Receiving message from other nodes
        and distribute it to others
        """
        message = request.message
        sender_id = request.sender_id
        received_timestamp = time.time_ns()

        # Check for message initiation and set the initial timestamp
        if sender_id == self.host and self.received_messages_time < received_timestamp:
            self.received_messages.add(message)
            log_message = (f"Gossip initiated by {self.host} at "
                           f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(received_timestamp / 1e9))}")
            self._log_event(message, sender_id, received_timestamp, None,
                            'initiate', log_message)

        # Check for duplicate messages
        elif message in self.received_messages:
            log_message = f"{self.host} ignoring duplicate message: {message} from {sender_id}"
            self._log_event(message, sender_id, received_timestamp, None,'duplicate', log_message)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by ({self.host})")

        # Send to message neighbor (that is  not receiving the message yet)
        else:
            self.received_messages.add(message)
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            log_message = (f"({self.host}) received: '{message}' from {sender_id}"
                           f" in {propagation_time:.2f} ms ")
            self._log_event(message, sender_id, received_timestamp, propagation_time, 'received', log_message)

        # Gossip to neighbors (only if the message is new)
        self.gossip_message(message, sender_id)
        return gossip_pb2.Acknowledgment(details=f"{self.pod_name}({self.host}) processed message: '{message}'")

    def gossip_message(self, message, sender_ip):
        # Refresh list of neighbors before gossiping to capture any changes
        self.get_neighbours()
        for peer_ip in self.susceptible_nodes:
            # Exclude the sender from the list of nodes to forward the message to
            if peer_ip != sender_ip:

                # Record the send timestamp
                send_timestamp = time.time_ns()

                with grpc.insecure_channel(f"{peer_ip}:5050") as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(
                            message=message,
                            sender_id=self.pod_name,
                            timestamp=send_timestamp,
                        ))
                    except grpc.RpcError as e:
                        print(f"Failed to send message: '{message}' to {peer_ip}: {e}", flush=True)

    def _log_event(self, message, sender_id, received_timestamp, propagation_time, event_type, log_message):
        """Logs the gossip event as structured JSON data."""
        event_data = {
            'message': message,
            'sender_id': sender_id,
            'receiver_id': self.host,
            'received_timestamp': received_timestamp,
            'propagation_time': propagation_time,
            'event_type': event_type,
            'detail': log_message
        }

        # Print both the log message and the JSON data to the console
        print(json.dumps(event_data), flush=True)

    def start_server(self):
        """ Initiating server """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"({self.host}) listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()

def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()

if __name__ == '__main__':
    run_server()