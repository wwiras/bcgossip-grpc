from kubernetes import client, config
import grpc
import os
import socket
from concurrent import futures
import gossip_pb2
import gossip_pb2_grpc
import json
import time
import pandas as pd
import pandas_gbq

class Node(gossip_pb2_grpc.GossipServiceServicer):
    def __init__(self, service_name):
        self.pod_name = socket.gethostname()
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

        # Set up BigQuery table ID (replace with your actual project ID)
        self.table_id = 'bcgossip-proj.gossip_simulation.gossip_events'

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
            self.initial_gossip_timestamp = pd.Timestamp.utcnow()
            print(f"Gossip initiated by {self.pod_name}({self.host}) at {self.initial_gossip_timestamp.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

            # Write initiate message event to BigQuery
            row_to_insert = {
                'message': message,
                'sender_id': sender_id,
                'receiver_id': self.pod_name,
                'received_timestamp': self.initial_gossip_timestamp,
                'propagation_time': None,
                'event_type': 'initiate'
            }
            self._insert_into_bigquery(row_to_insert)

        # Check for duplicate messages
        elif message in self.received_messages:
            # Write duplicate message event to BigQuery
            row_to_insert = {
                'message': message,
                'sender_id': sender_id,
                'receiver_id': self.pod_name,
                'received_timestamp': pd.Timestamp.utcnow(),
                'propagation_time': None,
                'event_type': 'duplicate'
            }
            self._insert_into_bigquery(row_to_insert)

            print(f"{self.pod_name}({self.host}) ignoring duplicate message: '{message}' from {sender_id}", flush=True)
            return gossip_pb2.Acknowledgment(details=f"Duplicate message ignored by {self.pod_name}({self.host})")

        else:
            self.received_messages.add(message)
            propagation_time = (received_timestamp - request.timestamp) / 1e6
            print(f"{self.pod_name}({self.host}) received: '{message}' from {sender_id} in {propagation_time:.2f} ms", flush=True)

            # Write received message event to BigQuery
            row_to_insert = {
                'message': message,
                'sender_id': sender_id,
                'receiver_id': self.pod_name,
                'received_timestamp': pd.Timestamp.utcnow(),
                'propagation_time': propagation_time,
                'event_type': 'received'
            }
            self._insert_into_bigquery(row_to_insert)

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

    def _insert_into_bigquery(self, row):
        """Inserts a row into BigQuery using pandas-gbq for convenience."""

        # Create a DataFrame with the row data
        df = pd.DataFrame([row])

        # Load the DataFrame into BigQuery using pandas-gbq
        try:
            pandas_gbq.to_gbq(df, self.table_id,
                              project_id='bcgossip-proj',
                              progress_bar=False,
                              if_exists='append')  # Replace 'your-project-id' with your actual project ID
            print(f"Loaded 1 row into {self.table_id}", flush=True)
        except pandas_gbq.gbq.GenericGBQException as e:
            print(f"Error inserting into BigQuery: {e}", flush=True)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", flush=True)


    def start_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gossip_pb2_grpc.add_GossipServiceServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{self.port}')
        print(f"{self.pod_name}({self.host}) listening on port {self.port}", flush=True)
        server.start()
        server.wait_for_termination()


def run_server():
    service_name = os.getenv('SERVICE_NAME', 'bcgossip')
    node = Node(service_name)
    node.start_server()


if __name__ == '__main__':
    run_server()
