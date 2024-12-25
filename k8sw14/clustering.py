import json, os
import numpy as np

def apply_agglomerative_clustering(nodes, num_clusters):
    """
    Applies agglomerative clustering to a network.
    Args:
      nodes: A list of nodes with their connections and latencies.
      num_clusters: The desired number of clusters.
    Returns:
      A list of clusters, where each cluster is a list of node IDs.
    """

    # 1. Create the distance matrix
    num_nodes = len(nodes)
    distance_matrix = np.zeros((num_nodes, num_nodes))
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            source_id = nodes[i]['id']
            target_id = nodes[j]['id']
            # Find the link between the two nodes (regardless of direction)
            latency = next((link['latency'] for link in links if (link['source'] == source_id and link['target'] == target_id) or (link['source'] == target_id and link['target'] == source_id)), np.inf)
            distance_matrix[i, j] = distance_matrix[j, i] = latency

    # 2. Initialize clusters with each node as a separate cluster
    clusters = [[node['id']] for node in nodes]

    # 3. Merge clusters iteratively
    while num_clusters < len(clusters):
        # Find the pair of clusters with minimum distance (complete linkage)
        min_dist = np.inf
        ci_index, cj_index = None, None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                # Use complete linkage to find the maximum distance between any two nodes in the clusters
                dist = max(distance_matrix[n1][n2] for n1 in clusters[i] for n2 in clusters[j])
                if dist < min_dist:
                    min_dist = dist
                    ci_index, cj_index = i, j

        # Merge the closest clusters
        cnew = clusters[ci_index] + clusters[cj_index]

        # Update the cluster set
        del clusters[max(ci_index, cj_index)]
        del clusters[min(ci_index, cj_index)]
        clusters.append(cnew)

        # Update the distance matrix (using complete linkage)
        new_distances = []
        for i in range(len(clusters) - 1):
            dist = max(distance_matrix[n1][n2] for n1 in clusters[i] for n2 in clusters[-1])
            new_distances.append(dist)
        distance_matrix = np.concatenate((distance_matrix[:-1], [new_distances]), axis=0)
        distance_matrix = np.concatenate((distance_matrix[:, :-1], np.array([new_distances]).T), axis=1)

    return clusters


# Construct the full file path
filepath = os.path.join('topology', 'nt_nodes11_RM.json')


# Load data from the JSON file
with open(filepath) as f:
    data = json.load(f)

nodes = data['nodes']
links = data['links']
num_clusters = 3  # Example: Create 3 clusters

# Apply agglomerative clustering
clusters = apply_agglomerative_clustering(10, 2)
print(clusters)