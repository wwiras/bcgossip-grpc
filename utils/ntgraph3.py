import networkx as nx
import json
import random
import uuid
import argparse


# The Purpose of this file is to create a network graph with a latency option


def generate_random_graph(num_nodes, probability, latency=None):
    """
    Generates a random network graph with optional constant or random latency.
    Ensures that every node has at least one neighbor.

    Args:
        num_nodes: The number of nodes in the graph.
        probability: The probability of an edge existing between any two nodes.
        latency: (Optional) If provided, all edges will have this constant latency.
                   If None, edges will have random latency from latency_options.

    Returns:
        A NetworkX graph object representing the generated graph.
    """
    G = nx.Graph()
    nodes = ['gossip-statefulset-' + str(i) for i in range(num_nodes)]
    G.add_nodes_from(nodes)

    # latency options
    # latency_map = {
    #     "pod-b": 10,  # 10 ms
    #     "pod-c": 100,  # 100 ms
    #     "pod-d": 300,  # 300 ms
    #     "pod-e": 500  # 500 ms
    # }
    latency_options = [10, 50, 100, 300]  # ms for milliseconds (used if latency is None)

    # Step 1: Ensure every node has at least one neighbor
    for i in range(num_nodes - 1):
        if latency is None:
            edge_latency = random.choice(latency_options)
        else:
            edge_latency = latency
        G.add_edge(nodes[i], nodes[i + 1], latency=edge_latency)

    # Connect the last node back to the first to ensure the graph is connected
    if num_nodes > 2:
        if latency is None:
            edge_latency = random.choice(latency_options)
        else:
            edge_latency = latency
        G.add_edge(nodes[num_nodes - 1], nodes[0], latency=edge_latency)

    # Step 2: Randomly add additional edges based on the given probability
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if not G.has_edge(nodes[i], nodes[j]) and random.random() < probability:
                if latency is None:
                    edge_latency = random.choice(latency_options)
                else:
                    edge_latency = latency
                G.add_edge(nodes[i], nodes[j], latency=edge_latency)

    return G


parser = argparse.ArgumentParser(description='Generate a random network graph and save its topology.')
parser.add_argument('--nodes', type=int, required=True, help='The number of nodes in the graph.')
parser.add_argument('--prob', type=float, required=True, help='The probability of an edge between two nodes (0.0 to 1.0).')
parser.add_argument('--latency', type=int, help='(Optional) Constant latency for all edges (in Mbps).')
args = parser.parse_args()

# Generate the random graph with optional latency
G = generate_random_graph(args.nodes, args.prob, args.latency)

# Generate a 5-character UUID
uuid_str = str(uuid.uuid4()).replace('-', '')[:5]

# Determine latency type for filename
latency_type = f"{args.latency}ms" if args.latency else "RL"  # 'rm' for random

# Create filename with nodes, probability, latency type, and UUID
filename = f'nt_nodes{args.nodes}_p{args.prob}_{latency_type}_{uuid_str}.json'

# Save the topology as JSON
topology = nx.node_link_data(G)
with open(filename, 'w') as outfile:
    json.dump(topology, outfile)