import networkx as nx
import json
import random
import uuid
import argparse

# def generate_random_graph(num_nodes, probability):
#     """
#     Generates a random network graph.
#
#     Args:
#         num_nodes: The number of nodes in the graph.
#         probability: The probability of an edge existing between any two nodes.
#
#     Returns:
#         A NetworkX graph object representing the generated graph.
#     """
#     G = nx.Graph()
#     nodes = ['gossip-statefulset-' + str(i) for i in range(num_nodes)]
#     G.add_nodes_from(nodes)
#
#     # Randomly add edges based on the given probability
#     for i in range(num_nodes):
#         for j in range(i + 1, num_nodes):
#             if random.random() < probability:
#                 G.add_edge(nodes[i], nodes[j])
#
#     # Ensure all nodes are connected
#     connected_components = list(nx.connected_components(G))
#     if len(connected_components) > 1:
#         for component in connected_components[1:]:  # Skip the first (largest) component
#             random_node_in_component = random.choice(list(component))
#             random_node_in_largest_component = random.choice(list(connected_components[0]))
#             G.add_edge(random_node_in_component, random_node_in_largest_component)
#
#     return G

# Parse command-line arguments

def generate_random_graph(num_nodes, probability):
    """
    Generates a random network graph with a partial ring structure.

    Args:
        num_nodes: The number of nodes in the graph.
        probability: The probability of an edge existing between any two nodes.

    Returns:
        A NetworkX graph object representing the generated graph.
    """
    G = nx.Graph()
    nodes = ['gossip-statefulset-' + str(i) for i in range(num_nodes)]
    G.add_nodes_from(nodes)

    # Create a partial ring (connect half of the nodes in a ring)
    ring_size = num_nodes // 2  # Integer division
    for i in range(ring_size - 1):
        G.add_edge(nodes[i], nodes[i + 1])
    if ring_size > 1:  # Connect the last node in the ring back to the first
        G.add_edge(nodes[ring_size - 1], nodes[0])

    # Randomly connect the remaining nodes to the ring or to each other
    for i in range(ring_size, num_nodes):
        for j in range(num_nodes):
            if i != j and random.random() < probability:
                G.add_edge(nodes[i], nodes[j])

    # Ensure all nodes are connected (in case some are still isolated)
    connected_components = list(nx.connected_components(G))
    if len(connected_components) > 1:
        for component in connected_components[1:]:
            random_node_in_component = random.choice(list(component))
            random_node_in_largest_component = random.choice(list(connected_components[0]))
            G.add_edge(random_node_in_component, random_node_in_largest_component)

    return G

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

# print(f"Network topology saved to {filename}")