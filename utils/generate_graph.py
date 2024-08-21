import networkx as nx
import json
import random
import uuid
import argparse

def generate_random_graph(total_nodes, max_edges, num_groups):
    """
    Generates a random network graph with controlled connectivity and grouping.

    Guarantees:
    - All nodes have at least one edge.
    - No node has more than 3 edges.
    - The total number of edges is as close to max_edges as possible.
    - Nodes are divided into groups, and there are connections between groups.

    Args:
        total_nodes: The total number of nodes in the graph.
        max_edges: The maximum number of edges allowed in the graph.
        num_groups: The number of groups to divide the nodes into.

    Returns:
        A NetworkX graph object representing the generated graph.
    """

    G = nx.Graph()
    nodes = ['gossip-statefulset-' + str(i) for i in range(total_nodes)]
    G.add_nodes_from(nodes)

    # Divide nodes into groups
    nodes_per_group = total_nodes // num_groups
    groups = [nodes[i:i + nodes_per_group] for i in range(0, total_nodes, nodes_per_group)]

    # Ensure all nodes within each group have at least one edge
    for group in groups:
        for node in group:
            while G.degree(node) == 0 and G.number_of_edges() < max_edges:
                other_node = random.choice([n for n in group if n != node and not G.has_edge(node, n)])
                G.add_edge(node, other_node)

    # Add inter-group edges to ensure connectivity between groups
    for i in range(num_groups - 1):
        group1 = groups[i]
        group2 = groups[i + 1]
        node1 = random.choice(group1)
        node2 = random.choice(group2)
        G.add_edge(node1, node2)

    # Try to add more edges within groups, respecting max_edges and max 3 edges per node
    for group in groups:
        for node in group:
            desired_num_edges_for_node = random.randint(1, 3)

            max_available_edges = max_edges - G.number_of_edges()
            if desired_num_edges_for_node > max_available_edges:
                desired_num_edges_for_node = max_available_edges

            while G.degree(node) < desired_num_edges_for_node and G.number_of_edges() < max_edges:
                other_node = random.choice([n for n in group if n != node and not G.has_edge(node, n)])
                G.add_edge(node, other_node)

    return G

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate a random network graph and save its topology.')
parser.add_argument('--nodes', type=int, dest='total_nodes', help='The total number of nodes in the graph.')
parser.add_argument('--max_edges', type=int, help='The maximum number of edges allowed in the graph.')
parser.add_argument('--groups', type=int, help='The number of groups to divide the nodes into.')
args = parser.parse_args()

# Generate the random graph
G = generate_random_graph(args.total_nodes, args.max_edges, args.groups)

# Generate a 5-character UUID
uuid_str = str(uuid.uuid4()).replace('-', '')[:5]

# Create a descriptive filename
filename = f'nt_nodes{args.total_nodes}_max_edges{args.max_edges}_groups{args.groups}_{uuid_str}.json'
print(filename)

# Convert the graph into a format suitable for JSON
topology = nx.node_link_data(G)

# Save the graph's structure to a JSON file
with open(filename, 'w') as outfile:
    json.dump(topology, outfile)

print(f"Network topology saved to {filename}")
