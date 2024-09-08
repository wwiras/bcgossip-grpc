import networkx as nx
import json
import random
import uuid
import argparse

def generate_random_graph(num_nodes, probability, bwidth=None):
    """
    Generates a random network graph with a partial ring structure and node bandwidths.
    """

    G = nx.Graph()
    nodes = [f'gossip-statefulset-{i}' for i in range(num_nodes)]
    G.add_nodes_from(nodes)

    # Create a partial ring
    ring_size = num_nodes // 2
    for i in range(ring_size - 1):
        G.add_edge(nodes[i], nodes[i + 1])
    if ring_size > 1:
        G.add_edge(nodes[ring_size - 1], nodes[0])

    # Randomly connect remaining nodes
    for i in range(ring_size, num_nodes):
        for j in range(num_nodes):
            if i != j and random.random() < probability:
                G.add_edge(nodes[i], nodes[j])

    # Ensure all nodes are connected
    connected_components = list(nx.connected_components(G))
    if len(connected_components) > 1:
        for component in connected_components[1:]:
            random_node_in_component = random.choice(list(component))
            random_node_in_largest_component = random.choice(list(connected_components[0]))
            G.add_edge(random_node_in_component, random_node_in_largest_component)

    # Assign bandwidths to nodes
    if bwidth:
        # Use the specified bandwidth for all nodes
        for node in nodes:
            G.nodes[node]['bandwidth'] = bwidth
    else:
        # Assign random bandwidths
        bandwidth_options = [1, 3, 5, 10]
        for node in nodes:
            G.nodes[node]['bandwidth'] = random.choice(bandwidth_options)

    return G

parser = argparse.ArgumentParser(description='Generate a random network graph and save its topology.')
parser.add_argument('--nodes', type=int, required=True, help='The number of nodes in the graph.')
parser.add_argument('--prob', type=float, required=True, help='The probability of an edge between two nodes (0.0 to 1.0).')
parser.add_argument('--bwidth', type=str, help='Optional bandwidth for all nodes (e.g., "1M"). If not provided, random bandwidths will be assigned.')
args = parser.parse_args()

# Generate the random graph
G = generate_random_graph(args.nodes, args.prob, args.bwidth)

# Generate a 5-character UUID
uuid_str = str(uuid.uuid4()).replace('-', '')[:5]

# Create filename with nodes, probability, and UUID
if args.bwidth:
    filename = f'nt_nodes{args.nodes}_p{args.prob}_{uuid_str}_{args.bwidth}.json'
else:
    filename = f'nt_nodes{args.nodes}_p{args.prob}_{uuid_str}.json'
print(filename)

# Save the topology as JSON
topology = nx.node_link_data(G)
with open(filename, 'w') as outfile:
    json.dump(topology, outfile)

# Save the topology as JSON
topology = nx.node_link_data(G)
with open(filename, 'w') as outfile:
    json.dump(topology, outfile, indent=2)