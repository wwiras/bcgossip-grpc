import numpy as np
import random

# Distance matrix (provided)
distance_matrix = np.array([
    [0, float('inf'), float('inf'), float('inf'), 50, float('inf'), float('inf'), 10, float('inf'), 10],
    [float('inf'), 0, 100, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'),
     float('inf')],
    [float('inf'), 100, 0, 50, float('inf'), 300, float('inf'), float('inf'), float('inf'), float('inf')],
    [float('inf'), float('inf'), 50, 0, 500, 100, float('inf'), float('inf'), float('inf'), float('inf')],
    [50, float('inf'), float('inf'), 500, 0, float('inf'), 10, float('inf'), 300, float('inf')],
    [float('inf'), float('inf'), 300, 100, float('inf'), 0, float('inf'), float('inf'), float('inf'), float('inf')],
    [float('inf'), float('inf'), float('inf'), float('inf'), 10, float('inf'), 0, float('inf'), float('inf'),
     float('inf')],
    [10, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), 0, 100, float('inf')],
    [float('inf'), float('inf'), float('inf'), float('inf'), 300, float('inf'), float('inf'), 100, 0, float('inf')],
    [10, float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'),
     0],
])

# Initial clusters (provided) - Using these as our data points
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


def k_medoids_clustering(distance_matrix, data_points, k, max_iterations=100):
    num_points = len(data_points)

    # 1. Initialization
    medoid_indices = random.sample(range(num_points), k)
    medoids = [data_points[i] for i in medoid_indices]

    clusters = {}

    for _ in range(max_iterations):
        # 2. Assignment step
        clusters = {medoid: [] for medoid in medoids}
        for i, point in enumerate(data_points):
            closest_medoid = None
            min_distance = float('inf')
            for j, medoid in enumerate(medoids):
                medoid_index = data_points.index(medoid)
                distance = distance_matrix[i][medoid_index]
                if distance < min_distance:
                    min_distance = distance
                    closest_medoid = medoid

            # Assign to the first medoid if all distances are inf
            if closest_medoid is None:
                closest_medoid = medoids[0]

            clusters[closest_medoid].append(point)

        # 3. Update step
        new_medoids = []
        for medoid, cluster_points in clusters.items():
            if not cluster_points:  # Handle empty clusters
                new_medoids.append(medoid)
                continue
            min_avg_distance = float('inf')
            best_medoid = medoid
            for potential_medoid in cluster_points:
                total_distance = 0
                for other_point in cluster_points:
                    total_distance += distance_matrix[data_points.index(potential_medoid)][
                        data_points.index(other_point)]
                avg_distance = total_distance / len(cluster_points) if len(cluster_points) > 0 else 0
                if avg_distance < min_avg_distance:
                    min_avg_distance = avg_distance
                    best_medoid = potential_medoid
            new_medoids.append(best_medoid)

        # Check for convergence
        if set(new_medoids) == set(medoids):
            break

        medoids = new_medoids

    return clusters


# Run the clustering
k = 3
print(f"distance_matrix:\n {distance_matrix}")
final_clusters = k_medoids_clustering(distance_matrix, data_points, k)

# Print the results
for medoid, cluster_points in final_clusters.items():
    print(f"Cluster with medoid {medoid}: {cluster_points}")