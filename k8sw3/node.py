from kubernetes import client, config
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
import json
import time
from google.cloud import bigquery

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):
        self.pod_name = socket.gethostname()  # Get the pod's name from the environment variable
        self.host = socket.gethostbyname(self.pod_name)
        self.port = '5050'
        self.service_name = service_name

        # Load the topology from the ConfigMap
        with open('/app/config/network_topology.json', 'r') as f:
            self.topology = json.load(f)

        # Find neighbors based on the topology
        self.neighbor_pod_names = self._find_neighbors(self.pod_name)
        print(f"{self.pod_name}({self.host}) neighbors: {self.neighbor_pod_names}", flush=True)

        self.received_messages = set()

        # Set up BigQuery client
        self.bigquery_client = bigquery.Client()
        self.table_id = 'bcgossip-proj.gossip_simulation.gossip_events'  # Replace with your actual table ID

        self.gossip_initiated = False
        self.initial_gossip_timestamp = None

    def get_pod_ip(self, pod_name, namespace="default"):
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.status.pod_ip

    def SendMessage(self, request, context):
        message = request.message
        sender_id = request.sender_id
        received_timestamp = time.time_ns()

        # Check for message initiation and set the initial timestamp
        if sender_id == self.pod_name and not self.gossip_initiated:
            self.gossip_initiated = True
            self.initial_gossip_timestamp = received_timestamp // 1000  # Convert to microseconds
            print(f"Gossip initiated by {self.pod_name}({self.host}) at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(received_timestamp / 1e9))}", flush=True)

            # Write initiate message event to BigQuery
            row_to_insert = {
                'message': message,
                'sender_id': sender_id,
                'receiver_id': self.pod_name,
                'received_timestamp': self.initial_gossip_timestamp,
                'propagation_time': None,  # No propagation time for initiated messages
                'event_type': 'initiate'
            }
            errors = self.bigquery_client.insert_rows_json(self.table_id, [row_to_insert])
            if errors == []:
                print("New rows have been added.")
            else:
                print("Encountered errors while inserting rows: {}".format(errors))

        # Check for duplicate messages
        elif message in self.received_messages:
            # Write duplicate message event to BigQuery
            row_to_insert = {
                'message': message,
                'sender_id': sender_id,
                'receiver_id': self.pod_name,
                'received_timestamp': received_timestamp // 1000,  # Convert to microseconds
                'propagation_time': None,
                'event_type': 'duplicate'
            }
            errors = self.bigquery_client.insert_rows_json(self.table_id, [row_to_insert])
            if errors == []:
                print("New rows have been added.")
            else:
                print("Encountered errors while inserting rows: {}".format(errors))

            print(f"{self.pod_name}({self.host}) ignoring duplicate message: '{message}' from {sender_id}", flush=True)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by {self.pod_name}({self.host})")
        else:
            self.received_messages.add(message)
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            print(f"{self.pod_name}({self.host}) received: '{message}' from {sender_id} in {propagation_time:.2f} ms", flush=True)

            # Convert nanosecond timestamp to microseconds for BigQuery
            received_timestamp_microseconds = received_timestamp // 1000

            # Write received message event to BigQuery
            row_to_insert = {
                'message': message,
                'sender_id': sender_id,
                'receiver_id': self.pod_name,
                'received_timestamp': received_timestamp_microseconds,  # Use microsecond timestamp
                'propagation_time': propagation_time,
                'event_type': 'received'
            }
            errors = self.bigquery_client.insert_rows_json(self.table_id, [row_to_insert])
            if errors == []:
                print("New rows have been added.")
            else:
                print("Encountered errors while inserting rows: {}".format(errors))

        # Gossip to neighbors (only if the message is new)
        self.gossip_message(message, sender_id, received_timestamp)
        return gossip_pb2.Acknowledgment(details=f"{self.pod_name}({self.host}) processed message: '{message}'")

    def gossip_message(self, message, sender_id, received_timestamp):
        for neighbor_pod_name in self.neighbor_pod_names:
            if neighbor_pod_name != sender_id:
                neighbor_ip = self.get_pod_ip(neighbor_pod_name)
                target = f"{neighbor_ip}:5050"
                with grpc.insecure_channel(target) as channel:
                    try:
                        stub = gossip_pb2_grpc.GossipServiceStub(channel)
                        stub.SendMessage(gossip_pb2.GossipMessage(
                            message=message,
                            sender_id=sender_id,
                            timestamp=received_timestamp
                        ))
                        print(f"{self.pod_name}({self.host}) forwarded message: '{message}' to {neighbor_pod_name} ({neighbor_ip})", flush=True)
                    except grpc.RpcError as e:
                        print(f"Failed to send message: '{message}' to {neighbor_pod_name}: {e}", flush=True)

    def _find_neighbors(self, node_id):
        """Identifies the neighbors of the given node based on the topology."""
        neighbors = []
        for link in self.topology['links']:
            if link['source'] == node_id:
                neighbors.append(link['target'])
            elif link['target'] == node_id:
                neighbors.append(link['source'])
        return neighbors

    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.pod_name}({self.host}) listening on port {self.port}", flush=True)  # Changed here
        server.start()
        server.wait_for_termination()


def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()


if __name__ == '__main__':
    run_server()
