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
max_distance = np.nanmax(distance_matrix[distance_matrix != np.inf])  # Get max finite distance
distance_matrix[distance_matrix == np.inf] = max_distance * 10  # Replace inf with a larger value

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