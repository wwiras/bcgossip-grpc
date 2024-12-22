import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import MDS

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

# 1. Replace inf with a large number
max_finite_distance = np.nanmax(distance_matrix[distance_matrix != np.inf])
large_distance = max_finite_distance * 10
distance_matrix_filled = np.nan_to_num(distance_matrix, posinf=large_distance)

# 2. Use MDS to transform the modified distance matrix
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42, normalized_stress="auto")
X_transformed = mds.fit_transform(distance_matrix_filled)

# 3. Apply KMeans
kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
kmeans.fit(X_transformed)
labels = kmeans.labels_

# 4. Create a dictionary to store cluster members
clusters = {i: [] for i in range(kmeans.n_clusters)}
for i, label in enumerate(labels):
    clusters[label].append(data_points[i])

# 5. Print the cluster assignments and members
for cluster_id, members in clusters.items():
    print(f"Cluster {cluster_id}:")
    for member in members:
        print(f"  - {member}")

# 6. Visualize the clusters (optional)
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 6))
plt.scatter(X_transformed[:, 0], X_transformed[:, 1], c=labels, s=50, cmap='viridis')

for i, point in enumerate(data_points):
    plt.annotate(point, (X_transformed[i, 0], X_transformed[i, 1]))

plt.title("K-means Clustering (2D Projection with MDS)")
plt.xlabel("Dimension 1")
plt.ylabel("Dimension 2")
plt.show()