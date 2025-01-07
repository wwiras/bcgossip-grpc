import networkx as nx
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os, json
import argparse
import numpy as np

class kMeans:  # Define the class correctly

    def __init__(self, filename, num_clusters):

        self.filename = filename
        self.num_clusters = num_clusters
        self.data = []
        self.num_nodes = 0
        self.distance_matrix = dict()
        self.distances = []
        self.graph = self.get_prev_graph()  # Build the graph in the constructor
        self.prev_weight_matrix = self.create_prev_weight_matrix() # Actual weight from prev graph
        self.create_weight_distances()  # Initialize distance (latency) matrix
        self.newgraph = nx.Graph() # Preparing new graph platform
        self.centroids_nodes = []
        self.clusters_members = []

    def get_prev_graph(self):
        """Loads JSON data from a file and creates a NetworkX graph."""

        # Get the current working directory
        current_directory = os.getcwd()

        # Construct the full path to the topology folder
        topology_folder = os.path.join(current_directory, "topology")

        # Load data from the JSON file
        with open(os.path.join(topology_folder, self.filename), 'r') as f:  # Use self.filename
            self.data = json.load(f)

        # Build graph (existing topology)
        graph = nx.Graph()
        # print(f"self.data['nodes']{self.data['nodes']}")
        for node in self.data['nodes']:
            # print(f"node['id']:{node['id']}")
            graph.add_node(node['id'])
        for edge in self.data['edges']:
            graph.add_edge(edge['source'], edge['target'], weight=edge['weight'])

        self.num_nodes = len(self.data['nodes'])

        return graph

    def create_prev_weight_matrix(self):

        nodes = self.data['nodes']
        edges = self.data['edges']
        dm = np.zeros((self.num_nodes, self.num_nodes))
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                source_id = nodes[i]['id']
                target_id = nodes[j]['id']
                weight = next((edge['weight'] for edge in edges if
                                (edge['source'] == source_id and edge['target'] == target_id) or (
                                        edge['source'] == target_id and edge['target'] == source_id)), np.inf)
                dm[i, j] = dm[j, i] = weight
        return dm

    def create_weight_distances(self):
        """Calculates best distances between the all nodes in the graph."""
        # 1. Calculate shortest path distances
        self.distance_matrix = dict(nx.all_pairs_dijkstra_path_length(self.graph))
        # print(f"self.distance_matrix:\n {self.distance_matrix}")
        self.distances = [[self.distance_matrix[n1][n2] for n2 in self.graph.nodes] for n1 in self.graph.nodes]
        # print(f"self.distances:\n {self.distances}")

    def get_kmeans_cluster(self):
        """
        Clusters a graph using k-means based on shortest path distances.

        Args:
            KMeans object
            self.graph: A NetworkX graph object.
            self.num_clusters: The desired number of clusters.

        Returns:
            A list of cluster assignments for each node in the graph.
        """

        # 1. Calculate shortest path distances
        # distance_matrix = dict(nx.all_pairs_dijkstra_path_length(self.graph))
        # print(f"distance_matrix:\n {distance_matrix}")
        # distances = [[distance_matrix[n1][n2] for n2 in self.graph.nodes] for n1 in self.graph.nodes]
        # print(f"distances:\n {distances}")

        # 2. Apply K-means clustering
        kmeans = KMeans(n_clusters=self.num_clusters, random_state=0, n_init="auto")
        kmeans.fit(self.distances)

        # Get cluster labels and centroids
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        # Find the closest nodes to the centroids
        centroid_nodes = []
        for centroid in centroids:
            # distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in self.weight_matrix]
            distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in self.distances]
            # print(f"distances_to_centroid: \n {distances_to_centroid}")
            closest_node_index = np.argmin(distances_to_centroid)
            # print(f"closest_node_index: \n {closest_node_index}")
            closest_node = list(self.graph.nodes)[closest_node_index]
            # print(f"closest_node: \n {closest_node}")
            centroid_nodes.append(closest_node)

        # Create a list to store the nodes in each cluster
        cluster_members = [[] for _ in range(self.num_clusters)]
        for i, label in enumerate(labels):
            cluster_members[label].append(list(self.graph.nodes)[i])

        self.cluster_members = cluster_members
        self.centroid_nodes = centroid_nodes

        # return labels, centroids, centroid_nodes, cluster_members
        # return labels

    def find_best_cluster_connector(self, clusters):
        """
        Finds the best cluster member to connect to a neighboring cluster
        based on shortest path distances.

        Args:
            clusters: A list of cluster assignments for each node.

        Returns:
            A dictionary where keys are cluster IDs and values are the best connector nodes.
        """

        best_connectors = {}
        for cluster_id in range(self.num_clusters):
            nodes_in_cluster = [node for i, node in enumerate(self.graph.nodes) if clusters[i] == cluster_id]

            # Calculate shortest path lengths to nodes in other clusters
            shortest_paths = {}
            for node in nodes_in_cluster:
                for other_cluster_id in range(self.num_clusters):
                    if other_cluster_id != cluster_id:
                        other_cluster_nodes = [n for i, n in enumerate(self.graph.nodes) if
                                               clusters[i] == other_cluster_id]
                        for other_node in other_cluster_nodes:
                            path_length = nx.shortest_path_length(self.graph, source=node, target=other_node,
                                                                  weight='weight')
                            shortest_paths.setdefault(node, {}).setdefault(other_cluster_id, []).append(path_length)

            # Find the node with the minimum average shortest path to other clusters
            min_avg_distance = float('inf')
            best_connector = None
            for node, distances in shortest_paths.items():
                avg_distance = np.mean([np.min(distances[other_cluster_id]) for other_cluster_id in distances])
                if avg_distance < min_avg_distance:
                    min_avg_distance = avg_distance
                    best_connector = node

            best_connectors[cluster_id] = best_connector

        return best_connectors

    def create_cluster_graph(self):

        # Create nodes based on each cluster
        # print(f"self.cluster_members: {self.cluster_members}")
        # print(f"len(self.cluster_members): {len(self.cluster_members)}")
        for clusterid, nodes in enumerate(self.cluster_members):
            # print(f"clusterid:{clusterid},{nodes}")
            # Add nodes to new graph
            for node in nodes:
                self.newgraph.add_node(node)

            # Add edges to new graph nodes with weight
            # if self cluster by itself no need to add edges
            if len(nodes) > 1:
                for n1 in nodes:
                    for n2 in nodes:
                        # ignore same nodes
                        if n1 == n2:
                            continue
                        else:
                            # Get edge data between nodes from previous graph
                            edge_data = self.graph.get_edge_data(n1, n2)
                            # if there is edge data from prev graph, get edge data
                            if edge_data is not None:
                                # if edge data not exist in new graph, add edge data
                                if not self.newgraph.get_edge_data(n1, n2):
                                    self.newgraph.add_edge(n1, n2,weight=edge_data['weight'])
                                    # print(f"New edge data between {n1} and {n2}: {edge_data} is added to new graph")
            # print(f"self.newgraph:{self.newgraph}")
        # print(f"nx.is_connected(self.newgraph) ? : {nx.is_connected(self.newgraph)}")



## Main code

# Get random topology file
parser = argparse.ArgumentParser(description="Create K-means clustering.")
parser.add_argument('--filename', required=True, help="Topology filename (Random gossip)")
parser.add_argument('--num_cluster', required=True, type=int, help="Number of clusters to build")
# Add the optional argument with a default value of False
parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
args = parser.parse_args()

# Get arguments from file input (filename and num_cluster)
kmeans = kMeans(args.filename, int(args.num_cluster))
print(f"args.filename: {args.filename}")
print(f"args.num_cluster: {args.num_cluster}")
# print(f"save : {args.save}")
# print(f"display : {args.display}")
# print(f"kmeans.num_nodes: {kmeans.num_nodes}")

# Get clusters from Kmeans
# clusters = kmeans.cluster_graph_kmeans()

# Perform clustering
# clusters, centroids, centroid_nodes, cluster_members = kmeans.cluster_graph_kmeans()
kmeans.get_kmeans_cluster()
# print(f"Clusters: \n {clusters}")
# print(f"Centroids: \n {centroids}")
print(f"Centroid Nodes: \n {kmeans.centroid_nodes}")
print(f"Cluster Members: \n {kmeans.cluster_members}")
print(f"len(cluster_members): \n {len(kmeans.cluster_members)}")

# Create new graph
kmeans.create_cluster_graph()

# Print the cluster assignments for each node
# for i, node in enumerate(kmeans.graph.nodes):
#     print(f"Node {node}: Cluster {clusters[i]}")

# Find the best cluster connectors
# best_connectors = kmeans.find_best_cluster_connector(clusters)
# print(f"Best Cluster Connectors: {best_connectors}")