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
        self.graph = self.get_prev_graph()  # Build the graph in the constructor
        self.weight_matrix = self.create_weight_matrix()  # Initialize distance (latency) matrix

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

    def create_weight_matrix(self):

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

    def cluster_nodes(self):
        """Clusters nodes using k-means on shortest path distances."""
        graph = self.graph

        # start kmeans here from weight matrix
        kmeans = KMeans(n_clusters=self.num_clusters, random_state=0, n_init="auto")
        kmeans.fit(self.weight_matrix)

        # Get cluster labels and centroids
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        # Find the closest nodes to the centroids
        centroid_nodes = []
        for centroid in centroids:
            distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in self.weight_matrix]
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
                    weight = self.weight_matrix[list(self.graph.nodes).index(node1)][
                        list(self.graph.nodes).index(node2)]
                    if weight != np.inf:  # Add edge only if there is a connection
                        new_graph.add_edge(node1, node2, weight=weight)

        # --- Centroid connections ---
        for i in range(len(centroid_nodes)):
            for j in range(i + 1, len(centroid_nodes)):
                node1 = centroid_nodes[i]
                node2 = centroid_nodes[j]
                weight = self.weight_matrix[list(self.graph.nodes).index(node1)][list(self.graph.nodes).index(node2)]
                if weight != np.inf:  # Add edge only if there is a connection
                    new_graph.add_edge(node1, node2, weight=weight)

        return new_graph

    def save_new_topology(self, graph):
        """Saves the topology to a JSON file with date and time in the filename."""
        # Create directory if it doesn't exist
        output_dir = "topology_kmeans"
        os.makedirs(output_dir, exist_ok=True)

        # Construct the full file path
        filename = f"kmeans_{self.filename[:-5]}_k{self.num_clusters}.json"
        file_path = os.path.join(output_dir, filename)

        # Convert the graph to a JSON-serializable format
        nodes = [{'id': node} for node in graph.nodes()]
        edges = [{'source': source, 'target': target, 'weight': data['weight']}
                 for source, target, data in graph.edges(data=True)]

        # Include 'directed', 'multigraph', and 'graph'
        graph_data = {
            'directed': False,
            'multigraph': False,
            'graph': {},
            'nodes': nodes,
            'edges': edges
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

        plt.show()

if __name__ == '__main__':

    """
        To run the code and display the topology (display=True):
        python convert_kmeans.py --filename nt_nodes10_Dec2820240043.json --num_cluster 3 --display

        To run the code and display the topology (display=False):
        python convert_kmeans.py --filename nt_nodes10_Dec2820240043.json --num_cluster 3
        """

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

    # latency (distance) matrix preview - optional
    print(f"kmeans.weight_matrix: \n {kmeans.weight_matrix}")

    # Perform clustering
    clusters, centroids, centroid_nodes, cluster_members = kmeans.cluster_nodes()
    print(f"Clusters: \n {clusters}")
    print(f"Centroids: \n {centroids}")
    print(f"Centroid Nodes: \n {centroid_nodes}")
    print(f"Cluster Members: \n {cluster_members}")
    print(f"len(cluster_members): \n {len(cluster_members)}")

    # Create new topology
    # new_graph = kmeans.create_new_topology(cluster_members, centroid_nodes)
    # print(f"new_graph: {new_graph}")

    # Display new topology
    # if args.display:
    #     kmeans.display_new_topology(new_graph, clusters, centroid_nodes)

    # Save new topology
    # if args.save:
    #     kmeans.save_new_topology(new_graph)