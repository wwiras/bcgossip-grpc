import networkx as nx
import json
import random
import uuid
import argparse

def generate_random_graph(num_nodes, probability):
    """
    Generates a random network graph.

    Args:
        num_nodes: The number of nodes in the graph.
        probability: The probability of an edge existing between any two nodes.

    Returns:
        A NetworkX graph object representing the generated graph.
    """
    G = nx.Graph()
    nodes = ['gossip-statefulset-' + str(i) for i in range(num_nodes)]
    G.add_nodes_from(nodes)

    # Randomly add edges based on the given probability
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < probability:
                G.add_edge(nodes[i], nodes[j])

    return G

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate a random network graph and save its topology.')
parser.add_argument('--nodes', type=int, help='The number of nodes in the graph.')
parser.add_argument('--prob', type=float, help='The probability of an edge between two nodes (0.0 to 1.0).')
args = parser.parse_args()

# Generate the random graph
G = generate_random_graph(args.nodes, args.prob)

# Generate a 5-character UUID
uuid_str = str(uuid.uuid4()).replace('-', '')[:5]

# Create filename with nodes, probability, and UUID
filename = f'nt_nodes{args.nodes}_p{args.prob}_{uuid_str}.json'
print(filename)

# Save the topology as JSON
topology = nx.node_link_data(G)
with open(filename, 'w') as outfile:
    json.dump(topology, outfile)

print(f"Network topology saved to {filename}")
