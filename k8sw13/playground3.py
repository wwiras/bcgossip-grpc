import numpy as np


def agglomerative_clustering(distance_matrix, nodes, desired_clusters):
    """
    Perform Agglomerative Clustering based on Complete Linkage.

    Parameters:
        distance_matrix (numpy.ndarray): Initial distance matrix.
        nodes (list): List of node labels.
        desired_clusters (int): Number of clusters to form.

    Returns:
        list: Final clusters.
    """
    # Initialize clusters, each node starts as its own cluster
    clusters = [[node] for node in nodes]

    while len(clusters) > desired_clusters:
        # Find the closest pair of clusters
        min_distance = float('inf')
        merge_idx1, merge_idx2 = -1, -1

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                # Compute the complete linkage distance between clusters
                cluster_i = clusters[i]
                cluster_j = clusters[j]
                max_distance = max(
                    distance_matrix[nodes.index(a)][nodes.index(b)]
                    for a in cluster_i for b in cluster_j
                )

                if max_distance < min_distance:
                    min_distance = max_distance
                    merge_idx1, merge_idx2 = i, j

        # Merge the closest clusters
        cluster1 = clusters.pop(merge_idx2)  # Pop the second cluster first to avoid reindexing
        cluster2 = clusters.pop(merge_idx1)
        new_cluster = cluster1 + cluster2
        clusters.append(new_cluster)

        # Update the distance matrix (complete linkage)
        for i in range(len(clusters) - 1):
            cluster_i = clusters[i]
            max_distance = max(
                distance_matrix[nodes.index(a)][nodes.index(b)]
                for a in cluster_i for b in new_cluster
            )
            distance_matrix[nodes.index(cluster_i[0])][nodes.index(new_cluster[0])] = max_distance
            distance_matrix[nodes.index(new_cluster[0])][nodes.index(cluster_i[0])] = max_distance

    return clusters


# Input Data
nodes = ["A", "B", "C", "D", "E"]
distance_matrix = np.array([
    [0, 2, 5, 3, 6],
    [2, 0, 4, 1, 7],
    [5, 4, 0, 8, 3],
    [3, 1, 8, 0, 5],
    [6, 7, 3, 5, 0]
], dtype=float)
desired_clusters = 3

# Perform Agglomerative Clustering
final_clusters = agglomerative_clustering(distance_matrix, nodes, desired_clusters)

# Output Final Clusters
print("Final Clusters:", final_clusters)
