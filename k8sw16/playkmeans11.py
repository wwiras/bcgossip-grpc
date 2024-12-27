# The latest kmeans playground
# It will be taking n of clusters (default is 3)
# and will output cluster(s)

import networkx as nx
from sklearn.cluster import KMeans
import random
import time
import matplotlib.pyplot as plt

# Load your JSON data
data = {
  "directed": False,
  "multigraph": False,
  "graph": {},
  "nodes": [
    {"id": "gossip-statefulset-0"},
    {"id": "gossip-statefulset-1"},
    {"id": "gossip-statefulset-2"},
    {"id": "gossip-statefulset-3"},
    {"id": "gossip-statefulset-4"},
    {"id": "gossip-statefulset-5"},
    {"id": "gossip-statefulset-6"},
    {"id": "gossip-statefulset-7"},
    {"id": "gossip-statefulset-8"},
    {"id": "gossip-statefulset-9"}
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

def create_graph_from_json(data):
    """Creates a NetworkX graph from JSON data."""
    graph = nx.Graph()
    for node in data['nodes']:
        graph.add_node(node['id'])
    for link in data['links']:
        graph.add_edge(link['source'], link['target'], weight=link['latency'])
    return graph

def cluster_nodes(graph, num_clusters):
    """Clusters nodes using k-means on shortest path distances."""
    distance_matrix = dict(nx.all_pairs_dijkstra_path_length(graph))
    distances = [[distance_matrix[n1][n2] for n2 in graph.nodes] for n1 in graph.nodes]
    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init="auto")
    kmeans.fit(distances)
    centroids = kmeans.cluster_centers_
    print(f"centroids : \n {centroids}")
    return kmeans.labels_

def gossip_protocol(graph, clusters, message):
    """Simulates gossip protocol with intra- and inter-cluster phases."""
    nodes = list(graph.nodes)
    num_nodes = len(nodes)
    infected = set()
    total_messages_sent = 0
    start_time = time.time()

    for cluster_id in range(max(clusters) + 1):
        cluster_nodes = [node for i, node in enumerate(nodes) if clusters[i] == cluster_id]
        if not cluster_nodes:
            continue
        initial_infected = random.choice(cluster_nodes)
        infected.add(initial_infected)
        current_infected = [initial_infected]
        while len(current_infected) > 0:
            new_infected = []
            for node in current_infected:
                neighbors = list(graph.neighbors(node))
                for neighbor in neighbors:
                    if neighbor not in infected and neighbor in cluster_nodes:
                        infected.add(neighbor)
                        new_infected.append(neighbor)
                        total_messages_sent += 1
            current_infected = new_infected

    while len(infected) < num_nodes:
        infected_node = random.choice(list(infected))
        neighbors = list(graph.neighbors(infected_node))
        for neighbor in neighbors:
            if neighbor not in infected:
                infected.add(neighbor)
                total_messages_sent += 1
                break

    end_time = time.time()
    propagation_time = end_time - start_time
    propagation_time_ms = (end_time - start_time) * 1000

    print(f"Propagation time: {propagation_time:.4f} seconds")
    print(f"Propagation time: {propagation_time_ms:.2f} milliseconds")
    redundancy = (total_messages_sent - num_nodes) / num_nodes if num_nodes > 0 else 0
    print(f"Message Redundancy: {redundancy:.2f}")

    for node in graph.nodes:
        neighbors = graph.neighbors(node)
        n = []
        for neighbor in neighbors:
            latency = graph[node][neighbor]['weight']
            n.append([neighbor, latency])
        print(f"Node: {node}, Neighbor: {n}")

# Create the graph
graph = create_graph_from_json(data)

# Cluster the nodes
num_clusters = 3
clusters = cluster_nodes(graph, num_clusters)
print(f"clusters : \n {clusters}")

# Simulate the gossip protocol
message = "Hello from the gossip protocol!"
gossip_protocol(graph, clusters, message)

# --- Visualize the clusters with edge weights (latency) ---

# Get edge weights for visualization
edge_weights = nx.get_edge_attributes(graph, 'weight')

# Draw the graph
plt.figure(figsize=(10, 8))  # Set figure size for better visibility

# Use a spring layout or another suitable layout algorithm
pos = nx.spring_layout(graph, seed=42)  # You can use other layouts like nx.spectral_layout, nx.shell_layout, etc.

# Draw nodes with colors based on cluster assignment
nx.draw_networkx_nodes(graph, pos, node_color=clusters, cmap=plt.cm.viridis, node_size=500)

# Draw node labels
nx.draw_networkx_labels(graph, pos)

# Draw edges with varying widths based on latency
edges = graph.edges()
# Scale edge widths for better visualization (thicker lines for higher latency)
edge_widths = [edge_weights[edge] / max(edge_weights.values()) * 5 for edge in edges]
nx.draw_networkx_edges(graph, pos, edgelist=edges, width=edge_widths, alpha=0.7)

# Add edge labels for latency
nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_weights, font_size=8)

plt.title("Network Graph with Clusters and Latency")
plt.axis('off')
plt.show()