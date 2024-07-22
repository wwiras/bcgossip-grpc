import grpc
import time
import random
import blockchain_pb2
import blockchain_pb2_grpc
from concurrent import futures
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer

# OpenTelemetry Setup
tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# gRPC Server Instrumentation
GrpcInstrumentorServer().instrument()


class BlockchainNode(blockchain_pb2_grpc.GossipServicer):
    def __init__(self, node_id, neighbors):
        self.node_id = node_id
        self.neighbors = neighbors
        self.server = None

        # --- Weight-Based Logic ---
        self.weights = {neighbor: 1.0 for neighbor in neighbors}
        self.latencies = {neighbor: 0 for neighbor in neighbors}

        # --- Blockchain Logic ---
        self.blockchain = []
        self.pending_transactions = []

    def update_weights(self):
        """Updates neighbor weights based on latency measurements."""
        for neighbor in self.neighbors:
            try:
                with grpc.insecure_channel(neighbor) as channel:
                    stub = blockchain_pb2_grpc.GossipStub(channel)
                    start_time = time.time_ns()
                    stub.GossipMessage(blockchain_pb2.Message(content="", timestamp=0))  # dummy message
                    end_time = time.time_ns()
                    self.latencies[neighbor] = end_time - start_time

            except grpc.RpcError as e:
                print(f"Error measuring latency to {neighbor}: {e}")
                self.latencies[neighbor] = float('inf')  # Set very high latency for failed connections

        total_latency = sum(self.latencies.values())
        for neighbor in self.neighbors:
            if total_latency > 0:  # Avoid division by zero
                self.weights[neighbor] = max(0.1, total_latency / (len(self.neighbors) * self.latencies[neighbor]))

    def choose_neighbor(self):
        """Chooses a neighbor for message relaying based on weights."""
        neighbors = list(self.weights.keys())
        weights = list(self.weights.values())
        return random.choices(neighbors, weights=weights)[0]  # Weighted random selection

    # ----- Blockchain-Specific Logic -----
    def validate_message(self, message):
        """Validates a received message."""
        # ... (Implement your message validation logic here)
        return True  # Placeholder, always returns true for now

    def add_message_to_blockchain(self, message):
        """Adds a validated message to the blockchain."""
        # ... (Implement your blockchain update logic here)
        self.blockchain.append(message)
        print(f"Node {self.node_id} added message '{message}' to blockchain.")
        print(f"Current blockchain: {self.blockchain}")

    # ---------------------------------------------------------

    def GossipMessage(self, request, context):
        with tracer.start_as_current_span("GossipMessage") as span:
            message = request.content
            timestamp = request.timestamp

            # --- Blockchain Logic ---
            if self.validate_message(message):
                self.add_message_to_blockchain(message)

            # --- Measure Propagation Time ---
            propagation_time = time.time_ns() - timestamp

            # --- Log Propagation Time (replace with your logging mechanism) ---
            print(f"Node {self.node_id} received message '{message}' (propagation time: {propagation_time} ns)")

            # --- Weight-Based Gossip Logic ---
            self.update_weights()
            neighbor = self.choose_neighbor()

            # --- Relay Message to Neighbor ---
            with grpc.insecure_channel(neighbor) as channel:
                stub = blockchain_pb2_grpc.GossipStub(channel)
                response = stub.GossipMessage(request)

        return blockchain_pb2.Empty()

    def serve(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        blockchain_pb2_grpc.add_GossipServicer_to_server(self, self.server)
        self.server.add_insecure_port('[::]:50051')
        self.server.start()
        print(f"Node {self.node_id} started listening on port 50051")
        self.server.wait_for_termination()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Blockchain Node")
    parser.add_argument("--node_id", type=int, required=True, help="Unique ID for the node")
    parser.add_argument("--neighbors", type=str, required=True, help="Comma-separated list of neighbor node IDs")
    args = parser.parse_args()

    neighbors = [f"{n}:50051" for n in args.neighbors.split(",")]  # Format neighbors as "node-X:50051"
    node = BlockchainNode(args.node_id, neighbors)
    node.serve()
