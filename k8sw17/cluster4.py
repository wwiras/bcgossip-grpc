import numpy as np


def initialize_centroids(data, k):
    """Randomly initialize k centroids from the data."""
    indices = np.random.choice(len(data), k, replace=False)
    return data[indices]


def assign_clusters(data, centroids):
    """Assign each data point to the nearest centroid."""
    distances = np.linalg.norm(data[:, np.newaxis] - centroids, axis=2)
    return np.argmin(distances, axis=1)


def update_centroids(data, labels, k):
    """Update centroid positions based on the mean of assigned points."""
    new_centroids = np.array([data[labels == i].mean(axis=0) for i in range(k)])
    return new_centroids


def kmeans(data, k, max_iters=100, tol=1e-4, random_state=None):
    """
    Manual implementation of K-Means clustering.

    Parameters:
    - data: NumPy array of shape (n_samples, n_features).
    - k: Number of clusters.
    - max_iters: Maximum number of iterations.
    - tol: Tolerance for convergence (based on centroid movement).
    - random_state: Seed for reproducibility.

    Returns:
    - centroids: Final centroids.
    - labels: Cluster assignments for each data point.
    """
    if random_state:
        np.random.seed(random_state)

    centroids = initialize_centroids(data, k)
    for i in range(max_iters):
        labels = assign_clusters(data, centroids)
        new_centroids = update_centroids(data, labels, k)

        # Check for convergence
        if np.linalg.norm(new_centroids - centroids) < tol:
            break
        centroids = new_centroids

    return centroids, labels


# Example Usage
if __name__ == "__main__":
    # Generate some sample data
    from sklearn.datasets import make_blobs

    data, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=42)

    # Run manual K-Means
    k = 3
    centroids, labels = kmeans(data, k, random_state=42)

    # Visualize the results
    import matplotlib.pyplot as plt

    plt.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', s=50)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='x', s=200, label='Centroids')
    plt.legend()
    plt.show()
