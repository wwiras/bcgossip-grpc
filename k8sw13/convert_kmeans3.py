import networkx as nx
from sklearn.cluster import KMeans
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
        self.latency_matrix = self.create_latency_matrix()  # Initialize distance (latency) matrix

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
        graph = self.graph

        # start kmeans here from latency matrix
        kmeans = KMeans(n_clusters=self.num_clusters, random_state=0, n_init="auto")
        kmeans.fit(self.latency_matrix)

        # Get cluster labels and centroids
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        # Find the closest nodes to the centroids
        centroid_nodes = []
        for centroid in centroids:
            distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in self.latency_matrix]
            # print(f"distances_to_centroid: \n {distances_to_centroid}")
            closest_node_index = np.argmin(distances_to_centroid)
            # print(f"closest_node_index: \n {closest_node_index}")
            closest_node = list(graph.nodes)[closest_node_index]
            # print(f"closest_node: \n {closest_node}")
            centroid_nodes.append(closest_node)

        # Create a list to store the nodes in each cluster
        cluster_members = [[] for _ in range(self.num_clusters)]
        for i, label in enumerate(labels):
            cluster_members[label].append(list(graph.nodes)[i])

        return labels, centroids, centroid_nodes, cluster_members

    def create_new_topology(self, cluster_members, centroid_nodes):
        """Creates a new topology with intra-cluster and centroid connections."""

        new_graph = nx.Graph()
        # Add nodes to the new graph
        for node in self.graph.nodes:
            new_graph.add_node(node)

        # --- Intra-cluster connections ---
        for cluster_id in range(self.num_clusters):
            nodes_in_cluster = cluster_members[cluster_id]
            for i in range(len(nodes_in_cluster)):
                for j in range(i + 1, len(nodes_in_cluster)):
                    node1 = nodes_in_cluster[i]
                    node2 = nodes_in_cluster[j]
                    latency = self.latency_matrix[list(self.graph.nodes).index(node1)][
                        list(self.graph.nodes).index(node2)]
                    if latency != np.inf:  # Add edge only if there is a connection
                        new_graph.add_edge(node1, node2, weight=latency)

        # --- Centroid connections ---
        for i in range(len(centroid_nodes)):
            for j in range(i + 1, len(centroid_nodes)):
                node1 = centroid_nodes[i]
                node2 = centroid_nodes[j]
                latency = self.latency_matrix[list(self.graph.nodes).index(node1)][list(self.graph.nodes).index(node2)]
                if latency != np.inf:  # Add edge only if there is a connection
                    new_graph.add_edge(node1, node2, weight=latency)

        return new_graph

    def save_new_topology(self, graph):
        """Saves the topology to a JSON file with date and time in the filename."""
        # Create directory if it doesn't exist
        output_dir = "topology_kmeans"
        os.makedirs(output_dir, exist_ok=True)

        # Get current date and time
        now = datetime.now()
        dt_string = now.strftime("%b%d%Y%H%M")  # Format: Dec2320241946

        # Construct the full file path
        filename = f"kmeans_{self.num_nodes}Nodes_k{self.num_clusters}_{dt_string}.json"
        file_path = os.path.join(output_dir, filename)

        # Convert the graph to a JSON-serializable format
        nodes = [{'id': node} for node in graph.nodes()]
        links = [{'source': source, 'target': target, 'latency': data['weight']}
                 for source, target, data in graph.edges(data=True)]

        # Include 'directed', 'multigraph', and 'graph'
        graph_data = {
            'directed': False,
            'multigraph': False,
            'graph': {},
            'nodes': nodes,
            'links': links
        }

        # Save the topology
        with open(file_path, 'w') as f:
            json.dump(graph_data, f, indent=4)

    def display_new_topology(self, new_graph, clusters, centroid_nodes):
        """Displays the new topology with colored clusters and centroid indicators."""

        # Get a list of node colors based on cluster assignment
        node_colors = [clusters[list(self.graph.nodes).index(node)] for node in new_graph.nodes()]

        # Get positions for nodes using a spring layout
        pos = nx.spring_layout(new_graph)

        # Draw the graph with colored nodes and edge labels
        nx.draw(new_graph, pos, with_labels=True, node_color=node_colors, cmap=plt.cm.viridis)
        labels = nx.get_edge_attributes(new_graph, 'weight')
        nx.draw_networkx_edge_labels(new_graph, pos, edge_labels=labels)

        # Highlight centroid nodes with bold labels
        # labels = {node: node if node not in centroid_nodes else f"**{node}**" for node in new_graph.nodes()}
        # nx.draw_networkx_labels(new_graph, pos, labels=labels, font_weight='bold')

        plt.show()

if __name__ == '__main__':

    # Get random topology file
    parser = argparse.ArgumentParser(description="Create K-means clustering.")
    parser.add_argument('--filename', required=True, help="Topology filename (Random gossip)")
    parser.add_argument('--num_cluster', required=True, type=int, help="Number of clusters to build")
    # Add the optional argument with a default value of False
    parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
    parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
    args = parser.parse_args()

    """
    To run the code and display the topology (display=True):
    python your_script.py --filename nt_nodes10_RM.json --num_cluster 2 --display
    
    To run the code and display the topology (display=False):
    python your_script.py --filename nt_nodes10_RM.json --num_cluster 2
    """

    # Get arguments from file input (filename and num_cluster)
    kmeans = kMeans(args.filename, args.num_cluster)
    print(f"args.filename: {args.filename}")
    print(f"args.num_cluster: {args.num_cluster}")
    print(f"save : {args.save}")
    print(f"display : {args.display}")
    print(f"kmeans.num_nodes: {kmeans.num_nodes}")

    # latency (distance) matrix preview - optional
    print(f"kmeans.latency_matrix: \n {kmeans.latency_matrix}")

    # Perform clustering
    clusters, centroids, centroid_nodes, cluster_members = kmeans.cluster_nodes()
    print(f"Clusters: \n {clusters}")
    print(f"Centroids: \n {centroids}")
    print(f"Centroid Nodes: \n {centroid_nodes}")
    print(f"Cluster Members: \n {cluster_members}")
    print(f"len(cluster_members): \n {len(cluster_members)}")

    # Create new topology
    new_graph = kmeans.create_new_topology(cluster_members, centroid_nodes)
    print(f"new_graph: {new_graph}")

    # Display new topology
    if args.display:
        kmeans.display_new_topology(new_graph, clusters, centroid_nodes)

    # Save new topology
    if args.save:
        kmeans.save_new_topology(new_graph)