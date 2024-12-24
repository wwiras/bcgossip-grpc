import networkx as nx
from sklearn.cluster import KMeans
import random
import time
import matplotlib.pyplot as plt
import os, json
import argparse
import numpy as np
from datetime import datetime

class kMeans:  # Define the class correctly

    def __init__(self, filename, num_clusters):
        self.filename = filename
        self.num_clusters = num_clusters
        self.data = []
        self.num_nodes = 0
        self.graph = self.get_prev_graph()  # Build the graph in the constructor
        self.latency_matrix = None  # Initialize the attribute

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
        for node in self.data['nodes']:
            graph.add_node(node['id'])
        for link in self.data['links']:
            graph.add_edge(link['source'], link['target'], weight=link['latency'])

        self.num_nodes = len(self.data['nodes'])

        return graph

    def create_latency_matrix(self):

        nodes = self.data['nodes']
        links = self.data['links']
        dm = np.zeros((self.num_nodes, self.num_nodes))
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                source_id = nodes[i]['id']
                target_id = nodes[j]['id']
                latency = next((link['latency'] for link in links if
                                (link['source'] == source_id and link['target'] == target_id) or (
                                        link['source'] == target_id and link['target'] == source_id)), np.inf)
                dm[i, j] = dm[j, i] = latency
        return dm

    def cluster_nodes(self):
        """Clusters nodes using k-means on shortest path distances."""
        ## There is something not right here.
        ## Please review
        graph = self.graph
        distance_matrix = dict(nx.all_pairs_dijkstra_path_length(graph))
        # print(f"distance_matrix: \n {distance_matrix}")

        path = dict(nx.all_pairs_shortest_path(graph))
        for key, value in path.items():
            print(f"key: {key}")
            print(f"value: {value}")

        distances = [[distance_matrix[n1][n2] for n2 in graph.nodes] for n1 in graph.nodes]
        print(f"distances: \n {distances}")

        kmeans = KMeans(n_clusters=self.num_clusters, random_state=0, n_init="auto")
        kmeans.fit(distances)

        # Get cluster labels and centroids
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        # Find the closest nodes to the centroids
        centroid_nodes = []
        for centroid in centroids:
            distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in distances]
            # print(f"distances_to_centroid: \n {distances_to_centroid}")
            closest_node_index = np.argmin(distances_to_centroid)
            # print(f"closest_node_index: \n {closest_node_index}")
            closest_node = list(graph.nodes)[closest_node_index]
            # print(f"closest_node: \n {closest_node}")
            centroid_nodes.append(closest_node)

        return labels, centroids, centroid_nodes


if __name__ == '__main__':

    # Step 1 - Get random topology file
    parser = argparse.ArgumentParser(description="Create K-means clustering.")
    parser.add_argument('--filename', required=True, help="Topology filename (Random gossip)")
    parser.add_argument('--num_cluster', required=True, type=int, help="Number of clusters to build")
    args = parser.parse_args()

    # Instantiate the kMeans class and pass filename and num_cluster
    kmeans = kMeans(args.filename, args.num_cluster)
    print(f"args.filename: {args.filename}")
    print(f"args.num_cluster: {args.num_cluster}")
    print(f"kmeans.num_nodes: {kmeans.num_nodes}")

    # Get latency prev matrix
    kmeans.latency_matrix = kmeans.create_latency_matrix()
    print(f"kmeans.latency_matrix: \n {kmeans.latency_matrix}")

    # Step 2 & 3 - Perform clustering
    # clusters = kmeans.cluster_nodes()
    # print(f"Clusters: \n {clusters}")
    clusters, centroids, centroid_nodes = kmeans.cluster_nodes()
    print(f"Clusters: \n {clusters}")
    print(f"Centroids: \n {centroids}")
    print(f"Centroid Nodes: \n {centroid_nodes}")



    # Test getting latency
    # print(f"kmeans.latency_matrix[0,1]: {kmeans.latency_matrix[0,1]}")
    # if kmeans.latency_matrix[0,1] == np.inf:
    #     print(f"kmeans.latency_matrix[0,1] is infinity / no connection")
    # print(f"kmeans.latency_matrix[0,4]: {kmeans.latency_matrix[0,4]}")
    # print(f"kmeans.latency_matrix[1,1]: {kmeans.latency_matrix[1,1]}")
    # print(f"np.isinf(kmeans.latency_matrix[0,1]) value is {np.isinf(kmeans.latency_matrix[0,1])}")
    # print(f"np.isinf(kmeans.latency_matrix[0,4] value is {np.isinf(kmeans.latency_matrix[0,4])}")
    # print(f"np.isinf(kmeans.latency_matrix[1,1]) value is {np.isinf(kmeans.latency_matrix[1,1])}")








    # Step 1 - Get random topology file
    # parser = argparse.ArgumentParser(description="Create K-means clustering.")
    # parser.add_argument('--filename', required=True, help="Topology filename (Random gossip)")
    # parser.add_argument('--num_cluster', required=True, help="Number of clusters to build")
    # args = parser.parse_args()
    # kmeans = kMeans(args.filename, int(args.num_cluster))
    # print(f"args.filename: {args.filename}")
    # print(f"int(args.num_cluster): {int(args.num_cluster)}")


    # Step 2 - Convert it to networkx (graph)
    # prev_graph = kmeans.get_prev_graph()
    # print(f"prev_graph: {prev_graph}")



    # Step 3 - Contruct new clusters (using K-means)
    # num_clusters = 3
    # num_clusters = int(args.num_cluster)
    # clusters = cluster_nodes(prev_graph, num_clusters)
    # print(f"Clusters : \n {clusters}")

    # Step 4 - Build new topology based on clusters
    # data_points = list(prev_graph.nodes)
    # num_nodes = len(data_points)
    # new_topology = create_new_topology(prev_graph, clusters, data_points)  # Pass prev_graph here

    # Step 5 - Save the new topology to a JSON file
    # save_topology_to_json(new_topology, num_nodes, num_clusters)