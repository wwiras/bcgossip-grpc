import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import MDS

# Distance matrix (provided) - 0 means no connection or self-connection
distance_matrix = np.array([
    [0, 0, 0, 0, 50, 0, 0, 10, 0, 10],
    [0, 0, 100, 0, 0, 0, 0, 0, 0, 0],
    [0, 100, 0, 50, 0, 300, 0, 0, 0, 0],
    [0, 0, 50, 0, 500, 100, 0, 0, 0, 0],
    [50, 0, 0, 500, 0, 0, 10, 0, 300, 0],
    [0, 0, 300, 100, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
    [10, 0, 0, 0, 0, 0, 0, 0, 100, 0],
    [0, 0, 0, 0, 300, 0, 0, 100, 0, 0],
    [10, 0, 0, 0, 0, 0, 0, 0, 0, 0],
])

# Data point names
data_points = [
    'gossip-statefulset-0',
    'gossip-statefulset-1',
    'gossip-statefulset-2',
    'gossip-statefulset-3',
    'gossip-statefulset-4',
    'gossip-statefulset-5',
    'gossip-statefulset-6',
    'gossip-statefulset-7',
    'gossip-statefulset-8',
    'gossip-statefulset-9',
]

print(f"distance_matrix before {distance_matrix}")

# 1. Replace 0s (no connection) with a large value for MDS
# Find the maximum finite distance
max_finite_distance = np.nanmax(distance_matrix[distance_matrix != 0])

# Replace 0s (no connection or self-connection) with a large value (e.g., 10 times the max distance)
# Also adding a small value to the diagonal to avoid 0s on the diagonal during MDS
large_distance = max_finite_distance * 10 + 1  # Add 1 to avoid 0 on diagonal
distance_matrix_filled = np.where(distance_matrix == 0, large_distance, distance_matrix)
print(f"distance_matrix_filled (after) {distance_matrix_filled}")
np.fill_diagonal(distance_matrix_filled, 0)  # Ensure diagonal is 0 for MDS

# 2. Use MDS to transform the distance matrix into a 2D representation
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=2, normalized_stress="auto")
X_transformed = mds.fit_transform(distance_matrix_filled)
print(f"X_transformed :\n {X_transformed}")

# 3. Apply KMeans
kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto")
kmeans.fit(X_transformed)
labels = kmeans.labels_

# 4. Print the cluster assignments
for i, label in enumerate(labels):
    print(f"{data_points[i]}: Cluster {label}")

# 5. Create a dictionary to store cluster members
clusters = {i: [] for i in range(kmeans.n_clusters)}
for i, label in enumerate(labels):
    clusters[label].append(data_points[i])

# 6. Print the cluster members
print("\nClusters and their members:")
for cluster_id, members in clusters.items():
    print(f"  Cluster {cluster_id}: {', '.join(members)}")

# # 7. Visualize the clusters (optional)
# import matplotlib.pyplot as plt
#
# plt.figure(figsize=(8, 6))
# plt.scatter(X_transformed[:, 0], X_transformed[:, 1], c=labels, s=50, cmap='viridis')
#
# for i, point in enumerate(data_points):
#     plt.annotate(point, (X_transformed[i, 0], X_transformed[i, 1]))
#
# plt.title("K-means Clustering (2D Projection with MDS)")
# plt.xlabel("Dimension 1")
# plt.ylabel("Dimension 2")
# plt.show()

# Find Medoids
cluster_medoids = {}
for cluster_id, members in clusters.items():
    member_indices = [data_points.index(member) for member in members]
    sub_matrix = distance_matrix[np.ix_(member_indices, member_indices)]
    avg_distances = np.mean(sub_matrix, axis=1)

    # Replace inf with a large number for medoid calculation
    avg_distances = np.where(avg_distances == float('inf'), max_finite_distance * 10, avg_distances)

    medoid_index = member_indices[np.argmin(avg_distances)]
    cluster_medoids[cluster_id] = data_points[medoid_index]

# Print Medoids
print("Cluster Medoids:")
for cluster_id, medoid in cluster_medoids.items():
    print(f"  Cluster {cluster_id}: {medoid}")


# Example of sending a message within a cluster:
def send_message_intra_cluster(source_node, message, cluster_id, medoid):
    print(f"\nSending message '{message}' from {source_node} within Cluster {cluster_id}:")
    if source_node != medoid:
        print(f"  1. {source_node} -> {medoid} (Medoid)")
    print(f"  2. {medoid} broadcasts to all nodes in Cluster {cluster_id}")


# Example usage
send_message_intra_cluster('gossip-statefulset-1', "Hello Cluster 0!", 0, cluster_medoids[0])