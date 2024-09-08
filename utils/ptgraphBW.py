import networkx as nx
import matplotlib.pyplot as plt
import json
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Visualize a network graph from a JSON file.')
parser.add_argument('--filename', type=str, help='The name of the JSON file containing the network topology.')
args = parser.parse_args()
print(args.filename)

# Load the topology
with open(args.filename, 'r') as f:
    topology = json.load(f)

# Create the graph
G = nx.node_link_graph(topology)

# Customize the plot
pos = nx.spring_layout(G)  # You can experiment with other layout algorithms if needed

# Extract node labels with bandwidth information
labels = {node: f"{node}\n({G.nodes[node]['bandwidth']} Mbps)" for node in G.nodes}

nx.draw(G, pos, with_labels=True, labels=labels, node_color='skyblue', node_size=800, font_size=8, font_color='black')

plt.title("Network Topology with Bandwidths")
plt.show()