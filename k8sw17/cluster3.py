import networkx as nx
import os
import json

# Create a simple graph with 5 nodes
# G = nx.Graph()
# nodes = [0, 1, 2, 3, 4]
# G.add_nodes_from(nodes)
#
# # Add some edges with weights
# G.add_edge(0, 1, weight=2)
# G.add_edge(0, 2, weight=5)
# G.add_edge(1, 2, weight=1)
# G.add_edge(1, 3, weight=3)
# G.add_edge(2, 3, weight=2)
# G.add_edge(2, 4, weight=4)
# G.add_edge(3, 4, weight=1)

# Get the current working directory
current_directory = os.getcwd()

# Construct the full path to the topology folder
topology_folder = os.path.join(current_directory, "topology")

# Load data from the JSON file
with open(os.path.join(topology_folder, "nodes10_Jan062025154931_ER0.4.json"), 'r') as f:  # Use self.filename
    data = json.load(f)

# Check if any edge has a 'weight' attribute
attribute = None
for edge in data['edges']:
    if 'weight' in edge:
        attribute='weight'
        break
    elif 'latency' in edge:
        attribute = 'latency'
        break

if attribute:
  print(f"The edges in the JSON file use '{attribute}' as the attribute.")
else:
  print("Neither 'weight' nor 'latency' found as edge attributes in the JSON file.")

# if data['edges']['latency']:
#     print(f"data['edges']['latency']: {data['edges']['latency']}")

# if data['edges']['weight']:
#     print(f"data['edges']['weight']: {data['edges']['weight']}")

# Build graph (existing topology)
G = nx.Graph()
# data = []
# print(f"self.data['nodes']{self.data['nodes']}")
for node in data['nodes']:
    # print(f"node['id']:{node['id']}")
    G.add_node(node['id'])
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], weight=edge['weight'])

num_nodes = len(data['nodes'])

# Calculate the distances matrix
distance_matrix = dict(nx.all_pairs_dijkstra_path_length(G))
distances = [[distance_matrix[n1][n2] for n2 in G.nodes] for n1 in G.nodes]
print(f"Distances Matrix:\n {distances}")


# Print the shortest path from node 6 to node 0
print(f"nx.shortest_path(G, source=0, target=6, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-0', target='gossip-statefulset-6', weight='weight')}")

# Print the shortest path from node 6 to node 0
print(f"nx.shortest_path(G, source=0, target=6, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-2', target='gossip-statefulset-6', weight='weight')}")

# Print the shortest path from node 5 to node 6
print(f"nx.shortest_path(G, source=5, target=6, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-5', target='gossip-statefulset-6', weight='weight')}")

# Print the shortest path from node 5 to node 6
print(f"nx.shortest_path(G, source=5, target=0, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-5', target='gossip-statefulset-0', weight='weight')}")

# Print the shortest path from node 5 to node 6
print(f"nx.shortest_path(G, source=8, target=6, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-8', target='gossip-statefulset-6', weight='weight')}")

# Print the shortest path from node 0 to node 1
print(f"nx.shortest_path(G, source=0, target=1, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-0', target='gossip-statefulset-1', weight='weight')}")


# Print the shortest path from node 0 to all other nodes
# p = nx.shortest_path(G, source=0, weight='weight')
# print(f"nx.shortest_path(G, source=0, weight='weight') \n {p}")

# Print the shortest path from all nodes to node 4
# p = nx.shortest_path(G, target=4, weight='weight')
# print(f"nx.shortest_path(G, target=4, weight='weight') \n {p}")

# Print the shortest path between all pairs of nodes
# p = dict(nx.shortest_path(G, weight='weight'))
# print(f"dict(nx.shortest_path(G, weight='weight') \n {p}")

