import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Create a graph with node features (allowing disconnected components)
def create_disconnected_graph():
    G = nx.Graph()
    # Add two disconnected components
    for i in range(5):  # First component
        G.add_node(i, feature=np.random.rand(2))
    for i in range(5, 10):  # Second component
        G.add_node(i, feature=np.random.rand(2))
    # Optionally add edges within components
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
    G.add_edges_from([(5, 6), (6, 7), (7, 8), (8, 9)])
    return G

# Step 2: K-Means for a single component
def kmeans_for_component(G, nodes, k, max_iterations=100):
    subgraph = G.subgraph(nodes)  # Work on the component subgraph
    centroids = random.sample(list(subgraph.nodes), k)
    for _ in range(max_iterations):
        clusters = assign_clusters(subgraph, centroids)
        new_centroids = update_centroids(subgraph, clusters)
        if set(new_centroids) == set(centroids):  # Check for convergence
            break
        centroids = new_centroids
    return clusters

# Step 3: Assign clusters and update centroids (same as before)
def assign_clusters(G, centroids):
    clusters = {centroid: [] for centroid in centroids}
    for node in G.nodes:
        distances = [
            np.linalg.norm(np.array(G.nodes[node]['feature']) - np.array(G.nodes[c]['feature']))
            for c in centroids
        ]
        nearest_centroid = centroids[np.argmin(distances)]
        clusters[nearest_centroid].append(node)
    return clusters

def update_centroids(G, clusters):
    new_centroids = []
    for centroid, nodes in clusters.items():
        if nodes:
            mean_feature = np.mean([G.nodes[node]['feature'] for node in nodes], axis=0)
            closest_node = min(nodes, key=lambda node: np.linalg.norm(G.nodes[node]['feature'] - mean_feature))
            new_centroids.append(closest_node)
    return new_centroids

def visualize_disconnected_clusters(G, all_clusters):
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    for i, (centroid, nodes) in enumerate(all_clusters.items()):
        node_features = np.array([G.nodes[node]['feature'] for node in nodes])
        plt.scatter(node_features[:, 0], node_features[:, 1], color=colors[i % len(colors)], label=f"Cluster {i+1}")
        centroid_feature = G.nodes[centroid]['feature']
        plt.scatter(centroid_feature[0], centroid_feature[1], color='black', marker='x', s=100, label=f"Centroid {i+1}")
    plt.legend()
    plt.show()

# Main execution
G = create_disconnected_graph()
connected_components = list(nx.connected_components(G))  # Find connected components
k = 2  # Number of clusters per component

# Apply K-Means to each component
all_clusters = {}
for component in connected_components:
    clusters = kmeans_for_component(G, component, k)
    all_clusters.update(clusters)

# Print results
for centroid, nodes in all_clusters.items():
    print(f"Centroid: {centroid}, Nodes: {nodes}")



# visualize_disconnected_clusters(G, all_clusters)