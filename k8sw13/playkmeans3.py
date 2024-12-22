import numpy as np
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
# distance_matrix[distance_matrix == np.inf] = None
print("distance_matrix:\n", distance_matrix)

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
print("kmeans:", kmeans)

# Print cluster assignments
print("Cluster assignments:", kmeans.labels_)
print("Cluster centers:", kmeans.predict(distance_matrix))
print("Inertia:", kmeans.inertia_)
print("Number of iterations:", kmeans.n_iter_)

# Re-arrange initial clusters based on K-means result
new_clusters = [[] for _ in range(num_clusters)]
for i, cluster_id in enumerate(kmeans.labels_):
  new_clusters[cluster_id].append(initial_clusters[i][0])

print("New clusters:", new_clusters)
print("Total clusters:", len(new_clusters))

def get_leader_node(cluster_id, clusters, distance_matrix):
  """Selects a leader node based on maximum distance to other clusters."""
  max_distance = float('-inf')
  leader_node = None
  for node_index in [i for i, label in enumerate(kmeans.labels_) if label == cluster_id]:
    # Calculate the minimum distance to nodes in other clusters
    min_distance_to_other_clusters = min(
        distance_matrix[node_index, j] for j, label in enumerate(kmeans.labels_) if label != cluster_id
    )
    # print(f"Leader node for cluster {cluster_id}: {initial_clusters[leader_node][0]}")
    if min_distance_to_other_clusters > max_distance:
      max_distance = min_distance_to_other_clusters
      leader_node = node_index
  return leader_node

# Select leader nodes for each cluster
leader_nodes = []
for cluster_id in range(len(new_clusters)):
  leader_node = get_leader_node(cluster_id, new_clusters, distance_matrix)
  leader_nodes.append(leader_node)
  print(f"Leader node for cluster {cluster_id}: {initial_clusters[leader_node][0]}")
