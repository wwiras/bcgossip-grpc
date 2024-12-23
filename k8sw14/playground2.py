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
        # for i in range(len(clusters) - 1):
        #     cluster_i = clusters[i]
        #     max_distance = max(
        #         distance_matrix[nodes.index(a)][nodes.index(b)]
        #         for a in cluster_i for b in new_cluster
        #     )
        #     distance_matrix[nodes.index(cluster_i[0])][nodes.index(new_cluster[0])] = max_distance
        #     distance_matrix[nodes.index(new_cluster[0])][nodes.index(cluster_i[0])] = max_distance

        for i in range(len(clusters) - 1):
            cluster_i = clusters[i]
            max_distance = max(
                distance_matrix[nodes.index(a)][nodes.index(b)]
                for a in cluster_i for b in new_cluster
            )
            # Update distances for all elements in the new cluster
            for node_new in new_cluster:
                distance_matrix[nodes.index(cluster_i[0])][nodes.index(node_new)] = max_distance
                distance_matrix[nodes.index(node_new)][nodes.index(cluster_i[0])] = max_distance

    return clusters


# Distance matrix
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

# Initial clusters
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

# Desired number of clusters
desired_clusters = 3

# Flatten the initial_clusters list to get the nodes list
nodes = [cluster[0] for cluster in initial_clusters]

# Perform Agglomerative Clustering
final_clusters = agglomerative_clustering(distance_matrix.copy(), nodes, desired_clusters)  # Use a copy of the distance matrix

# Output Final Clusters
print("Final Clusters:", final_clusters)