import networkx as nx
import matplotlib.pyplot as plt
import json
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Visualize a network graph from a JSON file.')
parser.add_argument('--filename', type=str, help='The name of the JSON file containing the network topology.')
args = parser.parse_args()
print(args.filename)

# Load the topology from the specified JSON file
with open(args.filename, 'r') as f:
    topology = json.load(f)

# Create a NetworkX graph from the topology data
G = nx.node_link_graph(topology)

# Customize the plot (optional)
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, font_size=10, font_color='black')
plt.title("Network Topology")
plt.show()
