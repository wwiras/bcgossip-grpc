import json
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
import matplotlib.pyplot as plt

# Load JSON data
data = """
{ 
  "directed": false,
  "multigraph": false,
  "graph": {},
  "nodes": [
    {"id": "gossip-statefulset-0"}, {"id": "gossip-statefulset-1"}, 
    {"id": "gossip-statefulset-2"}, {"id": "gossip-statefulset-3"}, 
    {"id": "gossip-statefulset-4"}, {"id": "gossip-statefulset-5"}, 
    {"id": "gossip-statefulset-6"}, {"id": "gossip-statefulset-7"}, 
    {"id": "gossip-statefulset-8"}, {"id": "gossip-statefulset-9"}
  ],
  "links": [
    {"source": "gossip-statefulset-0", "target": "gossip-statefulset-4", "latency": 50},
    {"source": "gossip-statefulset-0", "target": "gossip-statefulset-7", "latency": 10},
    {"source": "gossip-statefulset-0", "target": "gossip-statefulset-9", "latency": 10},
    {"source": "gossip-statefulset-1", "target": "gossip-statefulset-2", "latency": 100},
    {"source": "gossip-statefulset-2", "target": "gossip-statefulset-3", "latency": 50},
    {"source": "gossip-statefulset-2", "target": "gossip-statefulset-5", "latency": 300},
    {"source": "gossip-statefulset-3", "target": "gossip-statefulset-4", "latency": 500},
    {"source": "gossip-statefulset-3", "target": "gossip-statefulset-5", "latency": 100},
    {"source": "gossip-statefulset-4", "target": "gossip-statefulset-6", "latency": 10},
    {"source": "gossip-statefulset-4", "target": "gossip-statefulset-8", "latency": 300},
    {"source": "gossip-statefulset-7", "target": "gossip-statefulset-8", "latency": 100}
  ]
}
"""

graph_data = json.loads(data)

# Create graph
G = nx.Graph()
for node in graph_data["nodes"]:
    G.add_node(node["id"])
for link in graph_data["links"]:
    G.add_edge(link["source"], link["target"], latency=link["latency"])

# Feature extraction
features = []
nodes = list(G.nodes)
for node in nodes:
    degree = G.degree(node)
    avg_latency = (
        np.mean([G[node][neighbor]["latency"] for neighbor in G.neighbors(node)])
        if G[node] else 0
    )
    features.append([degree, avg_latency])


# Convert to numpy array
features = np.array(features)
print(f"features : \n {features}")

# Apply k-means
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(features)
print(f"clusters : \n {clusters}")

# Assign cluster labels to nodes
node_clusters = {node: cluster for node, cluster in zip(nodes, clusters)}
print(f"node_clusters : \n {node_clusters}")

# Visualize graph
colors = ['red', 'blue', 'green']
node_colors = [colors[node_clusters[node]] for node in nodes]

clusters_dict = defaultdict(list)
for node, cluster_id in node_clusters.items():
    clusters_dict[cluster_id].append(node)

# Gossip simulation
def simulate_gossip(G, clusters_dict, node_clusters, source_node):
    received = set()
    to_process = [source_node]

    # Simulate intra-cluster gossip
    cluster = node_clusters[source_node]
    cluster_nodes = clusters_dict[cluster]

    while to_process:
        current = to_process.pop(0)
        if current not in received:
            received.add(current)
            # Send to neighbors in the same cluster
            neighbors = [n for n in G.neighbors(current) if n in cluster_nodes]
            to_process.extend(neighbors)

    # Simulate inter-cluster gossip
    for cluster_id, nodes_in_cluster in clusters_dict.items():
        if cluster_id != cluster:
            # Send message to a representative node in the other cluster
            cluster_representative = nodes_in_cluster[0]  # Select representative
            if cluster_representative not in received:
                received.add(cluster_representative)
    return received


# Gossip simulation
# def simulate_gossip(G, node_clusters, source_node):
#     received = set()
#     to_process = [source_node]
#
#     # Simulate intra-cluster gossip
#     cluster = node_clusters[source_node]
#     cluster_nodes = [n for n in nodes if node_clusters[n] == cluster]
#
#     while to_process:
#         current = to_process.pop(0)
#         if current not in received:
#             received.add(current)
#             # Send to neighbors in the same cluster
#             neighbors = [n for n in G.neighbors(current) if n in cluster_nodes]
#             to_process.extend(neighbors)
#
#     # Simulate inter-cluster gossip
#     for cluster_id, nodes_in_cluster in node_clusters.items():
#         if cluster_id != cluster:
#             # Send message to cluster representatives
#             cluster_representative = nodes_in_cluster[0]  # Select representative
#             if cluster_representative not in received:
#                 received.add(cluster_representative)
#     return received

# Run gossip from a source node


# Run gossip from a source node
source_node = "gossip-statefulset-0"
received_nodes = simulate_gossip(G, clusters_dict, node_clusters, source_node)
print("Nodes that received the gossip:", received_nodes)

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500, font_size=10)
plt.show()