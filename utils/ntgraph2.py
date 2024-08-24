import networkx as nx
import json
import random
import uuid
import argparse


def generate_random_graph(num_nodes, probability, bandwidth=None):
    """
    Generates a random network graph with optional constant or random bandwidth.
    Ensures that every node has at least one neighbor.

    Args:
        num_nodes: The number of nodes in the graph.
        probability: The probability of an edge existing between any two nodes.
        bandwidth: (Optional) If provided, all edges will have this constant bandwidth.
                   If None, edges will have random bandwidth from bandwidth_options.

    Returns:
        A NetworkX graph object representing the generated graph.
    """
    G = nx.Graph()
    nodes = ['gossip-statefulset-' + str(i) for i in range(num_nodes)]
    G.add_nodes_from(nodes)

    # bandwidth options
    # Mbps  |   Kbps    | KB/s (Kilobytes per second) - official trickle bandwidth measurement
    # 1     |   1000    | 125
    # 3     |   3000    | 375
    # 5     |   5000    | 625
    # 10    |   10000   | 1250
    # For example:
    # 1 Mbps:
    # 1 Mbps * 1000 = 1000Kbps
    # 1000Kbps / 8 = 125KB/s
    bandwidth_options = [1, 3, 5, 10]  # Mbps (used if bandwidth is None)
    # bandwidth_options = [125, 375, 625, 1250]  # Kbps (used if bandwidth is None)

    # Step 1: Ensure every node has at least one neighbor
    for i in range(num_nodes - 1):
        if bandwidth is None:
            edge_bandwidth = random.choice(bandwidth_options)
        else:
            edge_bandwidth = bandwidth
        G.add_edge(nodes[i], nodes[i + 1], bandwidth=edge_bandwidth)

    # Connect the last node back to the first to ensure the graph is connected
    if num_nodes > 2:
        if bandwidth is None:
            edge_bandwidth = random.choice(bandwidth_options)
        else:
            edge_bandwidth = bandwidth
        G.add_edge(nodes[num_nodes - 1], nodes[0], bandwidth=edge_bandwidth)

    # Step 2: Randomly add additional edges based on the given probability
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if not G.has_edge(nodes[i], nodes[j]) and random.random() < probability:
                if bandwidth is None:
                    edge_bandwidth = random.choice(bandwidth_options)
                else:
                    edge_bandwidth = bandwidth
                G.add_edge(nodes[i], nodes[j], bandwidth=edge_bandwidth)

    return G


parser = argparse.ArgumentParser(description='Generate a random network graph and save its topology.')
parser.add_argument('--nodes', type=int, required=True, help='The number of nodes in the graph.')
parser.add_argument('--prob', type=float, required=True, help='The probability of an edge between two nodes (0.0 to 1.0).')
parser.add_argument('--bandwidth', type=int, help='(Optional) Constant bandwidth for all edges (in Mbps).')
args = parser.parse_args()

# Generate the random graph with optional bandwidth
G = generate_random_graph(args.nodes, args.prob, args.bandwidth)

# Generate a 5-character UUID
uuid_str = str(uuid.uuid4()).replace('-', '')[:5]

# Determine bandwidth type for filename
bandwidth_type = f"{args.bandwidth}M" if args.bandwidth else "RM"  # 'rm' for random
# KB for static bandwidth
# RKB for random bandwidth

# Create filename with nodes, probability, bandwidth type, and UUID
filename = f'nt_nodes{args.nodes}_p{args.prob}_{bandwidth_type}_{uuid_str}.json'

# Save the topology as JSON
topology = nx.node_link_data(G)
with open(filename, 'w') as outfile:
    json.dump(topology, outfile)