import json
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
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
    clustering_coeff = nx.clustering(G, node)
    features.append([degree, avg_latency, clustering_coeff])

# Convert to numpy array
features = np.array(features)

# Apply k-means
kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(features)

# Assign cluster labels to nodes
node_clusters = {node: cluster for node, cluster in zip(nodes, clusters)}

# Visualize graph
colors = ['red', 'blue', 'green']
node_colors = [colors[node_clusters[node]] for node in nodes]

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500, font_size=10)
plt.show()
