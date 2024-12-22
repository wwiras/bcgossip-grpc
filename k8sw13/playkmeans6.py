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

# --- K-means Clustering (using MDS as before) ---
print(f"  distance_matrix : \n {distance_matrix }")
max_finite_distance = np.nanmax(distance_matrix[distance_matrix != np.inf])
large_distance = max_finite_distance * 10
distance_matrix_filled = np.nan_to_num(distance_matrix, posinf=large_distance)

mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42, normalized_stress="auto")
X_transformed = mds.fit_transform(distance_matrix_filled)

kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
kmeans.fit(X_transformed)
labels = kmeans.labels_

clusters = {i: [] for i in range(kmeans.n_clusters)}
for i, label in enumerate(labels):
    clusters[label].append(data_points[i])

# --- Intra-Cluster Communication (Find Medoids) ---
cluster_medoids = {}
for cluster_id, members in clusters.items():
    member_indices = [data_points.index(member) for member in members]
    sub_matrix = distance_matrix[np.ix_(member_indices, member_indices)]
    avg_distances = np.mean(sub_matrix, axis=1)
    medoid_index = member_indices[np.argmin(avg_distances)]
    cluster_medoids[cluster_id] = data_points[medoid_index]

# --- Inter-Cluster Communication (Find Bridge Nodes) ---
cluster_bridges = {}
for cluster_id_1 in clusters.keys():
    cluster_bridges[cluster_id_1] = {}
    for cluster_id_2 in clusters.keys():
        if cluster_id_1 == cluster_id_2:
            continue

        min_dist = float('inf')
        best_pair = (None, None)

        for member_1 in clusters[cluster_id_1]:
            for member_2 in clusters[cluster_id_2]:
                idx_1 = data_points.index(member_1)
                idx_2 = data_points.index(member_2)
                dist = distance_matrix[idx_1][idx_2]

                if dist < min_dist:
                    min_dist = dist
                    best_pair = (member_1, member_2)

        cluster_bridges[cluster_id_1][cluster_id_2] = best_pair

# --- Print Results ---
print("Clusters and their members:")
for cluster_id, members in clusters.items():
    print(f"  Cluster {cluster_id}: {', '.join(members)}")

print("\nCluster Medoids (for intra-cluster communication):")
for cluster_id, medoid in cluster_medoids.items():
    print(f"  Cluster {cluster_id}: {medoid}")

print("\nCluster Bridges (for inter-cluster communication):")
for cluster_id_1 in clusters.keys():
    for cluster_id_2, (node_1, node_2) in cluster_bridges[cluster_id_1].items():
        print(f"  Between Cluster {cluster_id_1} and Cluster {cluster_id_2}: {node_1} <-> {node_2}")

# --- Example Message Propagation ---
def propagate_message(source_node, target_node, message):
    source_cluster = None
    target_cluster = None

    # Find the clusters of the source and target nodes
    for cluster_id, members in clusters.items():
        if source_node in members:
            source_cluster = cluster_id
        if target_node in members:
            target_cluster = cluster_id

    print(f"\nPropagating message '{message}' from {source_node} (Cluster {source_cluster}) to {target_node} (Cluster {target_cluster})")

    if source_cluster == target_cluster:
        # Intra-cluster propagation
        print(f"  1. {source_node} -> {cluster_medoids[source_cluster]} (Medoid)")
        print(f"  2. {cluster_medoids[source_cluster]} broadcasts to all nodes in Cluster {source_cluster}")
    else:
        # Inter-cluster propagation
        bridge_node_source = cluster_bridges[source_cluster][target_cluster][0]
        bridge_node_target = cluster_bridges[source_cluster][target_cluster][1]
        print(f"  1. {source_node} -> {cluster_medoids[source_cluster]} (Medoid)")
        print(f"  2. {cluster_medoids[source_cluster]} -> {bridge_node_source} (Bridge Node)")
        print(f"  3. {bridge_node_source} -> {bridge_node_target} (Bridge Node)")
        print(f"  4. {bridge_node_target} -> {cluster_medoids[target_cluster]} (Medoid)")
        print(f"  5. {cluster_medoids[target_cluster]} broadcasts to all nodes in Cluster {target_cluster}")


# Example Usage
propagate_message('gossip-statefulset-0', 'gossip-statefulset-5', "Hello from node 0!")
propagate_message('gossip-statefulset-8', 'gossip-statefulset-9', "Hello from node 8!")