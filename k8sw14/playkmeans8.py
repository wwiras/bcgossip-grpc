import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from sklearn.cluster import KMeans

# Distance matrix (provided)
distance_matrix = np.array([
    [0, float('inf'), float('inf'), float('inf'), 50, float('inf'), float('inf'), 10, float('inf'), 10],
    [float('inf'), 0, 100, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf')],
    [float('inf'), 100, 0, 50, float('inf'), 300, float('inf'), float('inf'), float('inf'), float('inf')],
    [float('inf'), float('inf'), 50, 0, 500, 100, float('inf'), float('inf'), float('inf'), float('inf')],
    [50, float('inf'), float('inf'), 500, 0, float('inf'), 10, float('inf'), 300, float('inf')],
    [float('inf'), float('inf'), 300, 100, float('inf'), 0, float('inf'), float('inf'), float('inf'), float('inf')],
    [float('inf'), float('inf'), float('inf'), float('inf'), 10, float('inf'), 0, float('inf'), float('inf'), float('inf')],
    [10, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, 100, float('inf')],
    [float('inf'), float('inf'), float('inf'), float('inf'), 300, float('inf'), float('inf'), 100, 0, float('inf')],
    [10, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0],
])

# Replace 'inf' with a large finite value
max_distance = np.nanmax(distance_matrix[distance_matrix != np.inf])
distance_matrix[distance_matrix == np.inf] = max_distance * 10

# Initial clusters (provided)
initial_clusters = [
    ['gossip-statefulset-0'],
    ['gossip-statefulset-1'],
    ['gossip-statefulset-2'],
    ['gossip-statefulset-3'],
    ['gossip-statefulset-4'],
    ['gossip-statefulset-5'],
    ['gossip-statefulset-6'],
    ['gossip-statefulset-7'],
    ['gossip-statefulset-8'],
    ['gossip-statefulset-9'],
]

def perform_clustering(distance_matrix, num_clusters):
  """Performs K-means clustering."""
  kmeans = KMeans(n_clusters=num_clusters, random_state=0)
  kmeans.fit(distance_matrix)
  return kmeans

# Perform K-means clustering
num_clusters = 3  # Example number of clusters
kmeans = perform_clustering(distance_matrix, num_clusters)

# Print cluster assignments
print("Cluster assignments:", kmeans.labels_)

# Re-arrange initial clusters based on K-means result
new_clusters = [[] for _ in range(num_clusters)]
for i, cluster_id in enumerate(kmeans.labels_):
  new_clusters[cluster_id].append(initial_clusters[i][0])

print("New clusters:", new_clusters)
print("Total clusters:", len(new_clusters))

# --- Construct Minimum Spanning Tree (MST) ---

def build_mst(distance_matrix):
  """Builds a minimum spanning tree from the distance matrix."""
  mst = minimum_spanning_tree(distance_matrix)
  return mst.toarray()  # Convert to a dense NumPy array

# Build the MST
mst_matrix = build_mst(distance_matrix)

# --- Build Network Graph with MST and K-means ---

# def build_network_graph(nodes, kmeans, mst_matrix):
#   """Builds a network graph with intra-cluster neighbors and MST connections."""
#   graph = {}
#   for node_index, node in enumerate(nodes):
#     cluster_id = kmeans.labels_[node_index]
#     neighbors = []
#
#     # Add intra-cluster neighbors
#     for other_node_index, other_node in enumerate(nodes):
#       if other_node_index != node_index and kmeans.labels_[other_node_index] == cluster_id:
#         neighbors.append(other_node)
#
#     # Add neighbors from MST
#     for other_node_index, distance in enumerate(mst_matrix[node_index]):
#       if distance > 0 and other_node_index != node_index:  # Connected in MST
#         neighbors.append(nodes[other_node_index])
#
#     graph[node] = neighbors
#   return graph

# --- Build Network Graph with MST and K-means ---

# def build_network_graph(nodes, kmeans, mst_matrix):
#   """Builds a network graph with intra-cluster neighbors and MST connections."""
#   graph = {}
#   for node_index, node in enumerate(nodes):
#     cluster_id = kmeans.labels_[node_index]
#     neighbors = set()  # Use a set to avoid duplicate neighbors
#
#     # Add intra-cluster neighbors
#     for other_node_index, other_node in enumerate(nodes):
#       if other_node_index != node_index and kmeans.labels_[other_node_index] == cluster_id:
#         neighbors.add(other_node)
#
#     # Add neighbors from MST
#     for other_node_index, distance in enumerate(mst_matrix[node_index]):
#       if distance > 0 and other_node_index != node_index:
#         neighbors.add(nodes[other_node_index])
#
#     graph[node] = list(neighbors)  # Convert back to a list
#   return graph

def build_network_graph(nodes, kmeans, mst_matrix, distance_matrix):  # Add distance_matrix as argument
    """Builds a network graph with intra-cluster neighbors and MST connections."""
    graph = {}
    for node_index, node in enumerate(nodes):
        cluster_id = kmeans.labels_[node_index]
        neighbors = set()  # Use a set to avoid duplicate neighbors

        # Add intra-cluster neighbors
        for other_node_index, other_node in enumerate(nodes):
            if other_node_index != node_index and kmeans.labels_[other_node_index] == cluster_id:
                neighbors.add(other_node)

        # Add neighbors from MST (corrected)
        for other_node_index, distance in enumerate(mst_matrix[node_index]):
            # Check if there is a connection in the MST and it's not infinity in the original distance matrix
            if distance > 0 and other_node_index != node_index and distance_matrix[node_index, other_node_index] != float('inf'):
                neighbors.add(nodes[other_node_index])

        graph[node] = list(neighbors)  # Convert back to a list
    return graph

# --- Flatten initial_clusters to get nodes ---
nodes = [cluster[0] for cluster in initial_clusters]

# Build the network graph
# network_graph = build_network_graph(nodes, kmeans, mst_matrix)

# Build the network graph (pass distance_matrix as argument)
network_graph = build_network_graph(nodes, kmeans, mst_matrix, distance_matrix)

# Print the network graph
for node, neighbors in network_graph.items():
  print(f"{node}: {neighbors}")