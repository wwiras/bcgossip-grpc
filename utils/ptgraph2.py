import networkx as nx
import matplotlib.pyplot as plt
import json
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Visualize a network graph from a JSON file.')
parser.add_argument('--filename', type=str, help='The name of the JSON file containing the network topology.')
args = parser.parse_args()

# Load the topology from the specified JSON file
with open(args.filename, 'r') as f:
    topology = json.load(f)

# Create a NetworkX graph from the topology data
G = nx.node_link_graph(topology)

# Extract bandwidth information for edge labels
edge_labels = nx.get_edge_attributes(G, 'bandwidth')
for (u, v) in edge_labels:
    edge_labels[(u, v)] = f"{edge_labels[(u, v)]} Kbps"

# Customize the plot with edge labels showing bandwidth (smaller font size)
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, font_size=10, font_color='black')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)  # Reduce font_size here

plt.title("Network Topology with Bandwidth Labels")
plt.show()