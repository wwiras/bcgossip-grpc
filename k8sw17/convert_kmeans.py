import networkx as nx
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os, json
import argparse
import numpy as np
import time


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
        self.clusters = []
        self.start_time = 0 # Get clustering start time
        self.end_time_kmeans = 0 # Get kmeans completed time
        self.end_time_all = 0 # Get all cluster establishment (connection) completed time

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

        self.start_time = time.time()  # Record start time

        # 2. Apply K-means clustering
        kmeans = KMeans(n_clusters=self.num_clusters, random_state=0, n_init="auto")
        kmeans.fit(self.distances)

        # Get cluster labels and centroids
        labels = kmeans.labels_
        self.end_time_kmeans = (time.time() - self.start_time) * 1000  # Calculate time in milliseconds

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
        self.clusters = labels

        # return labels, centroids, centroid_nodes, cluster_members
        # return labels

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

    def create_cluster_connectors(self):
        all_connected = False
        for cen in self.centroid_nodes:
            for cen_others in self.centroid_nodes:
                if not all_connected:
                    if cen is not cen_others:

                        # Get shortest path (with node sequence)
                        shortest_path = nx.shortest_path(self.graph, source=cen, target=cen_others, weight='weight')
                        # print(f"nx.shortest_path(self.graph, source={cen}, target={cen_others}, weight='weight') \n {shortest_path}")

                        # Crawl or iterate through the shortest path
                        # Iterate up to the second-to-last element
                        for i in range(len(shortest_path ) - 1):
                            current_node = shortest_path [i]
                            next_node = shortest_path [i + 1]
                            # print(f'self.newgraph.get_edge_data({current_node}, {next_node}):{self.newgraph.get_edge_data(current_node, next_node)}')

                            # Check whether there is connection between
                            # two nodes in the path (crawler)
                            # If no edge (None). So add edge
                            if self.newgraph.get_edge_data(current_node, next_node) is None:
                                edge_data = self.graph.get_edge_data(current_node, next_node)
                                self.newgraph.add_edge(current_node, next_node, weight=edge_data['weight'])
                                # print(f'self.newgraph.get_edge_data({current_node},{next_node}):{self.newgraph.get_edge_data(current_node,next_node)}')

                                # Check new graph whether all nodes are connected
                                if nx.is_connected(self.newgraph):
                                    all_connected = True
                                    break
        self.end_time_all = (time.time() - self.start_time) * 1000  # Calculate time in milliseconds
        return all_connected
    def display_new_topology(self):
        """Displays the new topology with colored clusters and centroid indicators."""
        # Create a dictionary to map node to cluster
        node_to_cluster = {}
        for cluster_id, members in enumerate(self.cluster_members):
            for node in members:
                node_to_cluster[node] = cluster_id
        # print(f'node_to_cluster:\n {node_to_cluster}')

        # Get a list of node colors based on cluster assignment
        node_colors = [node_to_cluster[node] for node in self.newgraph.nodes()]

        # Get positions for nodes using a spring layout
        pos = nx.spring_layout(self.newgraph)

        # Draw the graph with colored nodes and edge labels
        nx.draw(self.newgraph, pos, with_labels=True, node_color=node_colors, cmap=plt.cm.viridis)
        labels = nx.get_edge_attributes(self.newgraph, 'weight')
        nx.draw_networkx_edge_labels(self.newgraph, pos, edge_labels=labels)

        plt.show()

    def save_new_topology(self):
        """Saves the topology to a JSON file with date and time in the filename."""
        # Create directory if it doesn't exist
        output_dir = "topology_kmeans"
        os.makedirs(output_dir, exist_ok=True)

        # Construct the full file path
        filename = f"kmeans_{self.filename[:-5]}_k{self.num_clusters}.json"
        file_path = os.path.join(output_dir, filename)

        # Convert the graph to a JSON-serializable format with cluster labels
        nodes = [{'id': node, 'cluster': int(self.clusters[i])} for i, node in enumerate(self.graph.nodes())]
        # print(f"nodes={nodes}")
        edges = [{'source': source, 'target': target, 'weight': data['weight']}
                 for source, target, data in self.newgraph.edges(data=True)]

        # Include 'directed', 'multigraph', and 'graph'
        graph_data = {
            'directed': False,
            'multigraph': False,
            # Add clustering time as a comment (disabled by default)
            'kmeans_clustering_time_ms': self.end_time_kmeans,
            'total_clustering_time_ms': self.end_time_all,
            'graph': {},
            'nodes': nodes,
            'edges': edges
        }

        # Save the topology
        with open(file_path, 'w') as f:
            json.dump(graph_data, f, indent=4)

## Main code

# Get random topology file
parser = argparse.ArgumentParser(description="Create K-means clustering.")
parser.add_argument('--filename', required=True, help="Topology filename (Random gossip)")
parser.add_argument('--num_cluster', required=True, type=int, help="Number of clusters to build")
# Add the optional argument with a default value of False
parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
args = parser.parse_args()


### Below is the steps to create clusters from a ER or BA network model

# 1. Get arguments from file input (filename and num_cluster) - info first
kmeans = kMeans(args.filename, int(args.num_cluster))
print(f"args.filename: {args.filename}")
print(f"args.num_cluster: {args.num_cluster}")
# print(f"save : {args.save}")
# print(f"display : {args.display}")
# print(f"kmeans.num_nodes: {kmeans.num_nodes}")

# 2. Perform clustering / divides to cluster
kmeans.get_kmeans_cluster()
print(f"kmeans.clusters: \n {kmeans.clusters[0]}")
# print(f"Centroids: \n {centroids}")
# print(f"Centroid Nodes: \n {kmeans.centroid_nodes}")
print(f"Cluster Members: \n {kmeans.cluster_members}")
print(f"len(cluster_members): \n {len(kmeans.cluster_members)}")

# 3. Create new graphs (or groups) for the clusters created
kmeans.create_cluster_graph()

# 4. Connecting all clusters
if kmeans.create_cluster_connectors():
    # print(f"kmeans.newgraph:{kmeans.newgraph}")
    print("Creating connectors is successful")
    print(f"nx.is_connected(kmeans.newgraph) ? : {nx.is_connected(kmeans.newgraph)}")
else:
    print("Fail creating connectors")
    print(f"nx.is_connected(kmeans.newgraph) ? : {nx.is_connected(kmeans.newgraph)}")

## Options to display or save
# display kmeans cluster new topology
if args.display:
    kmeans.display_new_topology()

# save kmeans topology
if args.save:
    kmeans.save_new_topology()

