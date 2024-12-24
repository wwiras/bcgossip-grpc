import networkx as nx
from sklearn.cluster import KMeans
import random
import time
import matplotlib.pyplot as plt
import os, json
import argparse
import numpy as np
from datetime import datetime

"""
This script (convert_kmeans.py) is used to convert topology from 
(random gossip) to K-means influenced topology.
Below are the steps to execute it.
#1 - Runs the K-means clustering through convert_kmeans.py
     Accept topology (random gossip) as argument (filename in json format)
#2 - Convert it to networkx (graph) together with it latency
#3 - Contruct new clusters (using K-means)
#4 - convert the clusters to networkx (graph) as new json file 
Optional
## Print nodes and its new neighbor (with latency between)
## Show new cluster topology and latency
"""

class kMeans:  # Define the class correctly

    def __init__(self, filename, num_clusters):
        self.filename = filename
        self.num_clusters = num_clusters
        self.data = []
        self.num_nodes = 0
        self.graph = self.get_prev_graph()  # Build the graph in the constructor
        self.prev_latency_matrix = None  # Initialize the attribute

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

    def cluster_nodes(self):
        """Clusters nodes using k-means on shortest path distances."""
        graph = self.graph
        distance_matrix = dict(nx.all_pairs_dijkstra_path_length(graph))

        # Store the distance matrix
        self.prev_distance_matrix = distance_matrix

        distances = [[distance_matrix[n1][n2] for n2 in graph.nodes] for n1 in graph.nodes]
        kmeans = KMeans(n_clusters=self.num_clusters, random_state=0, n_init="auto")
        kmeans.fit(distances)
        return kmeans.labels_

    def create_prevlatency_matrix(self):

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
    kmeans.prev_latency_matrix = kmeans.create_prevlatency_matrix()
    print(f"kmeans.prev_latency_matrix: \n {kmeans.prev_latency_matrix}")

    # Step 2 & 3 - Perform clustering
    # clusters = kmeans.cluster_nodes()
    # print(f"Clusters: \n {clusters}")

    # Access the stored distance matrix (for example)
    # print(f"Previous Distance Matrix:\n {kmeans.prev_distance_matrix}")








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