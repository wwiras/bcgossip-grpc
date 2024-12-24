import networkx as nx
from sklearn.cluster import KMeans
import random
import time
import matplotlib.pyplot as plt
import os, json
import argparse
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

def get_prev_graph(filename):
    """Loads JSON data from a file and creates a NetworkX graph."""

    # Get the current working directory
    current_directory = os.getcwd()

    # Construct the full path to the topology folder
    topology_folder = os.path.join(current_directory, "topology")

    # Load data from the JSON file
    with open(os.path.join(topology_folder, filename), 'r') as f:
        data = json.load(f)

    # Build graph (existing topology)
    graph = nx.Graph()
    for node in data['nodes']:
        graph.add_node(node['id'])
    for link in data['links']:
        graph.add_edge(link['source'], link['target'], weight=link['latency'])
    return graph

def cluster_nodes(graph, num_clusters):
    """Clusters nodes using k-means on shortest path distances."""
    distance_matrix = dict(nx.all_pairs_dijkstra_path_length(graph))
    distances = [[distance_matrix[n1][n2] for n2 in graph.nodes] for n1 in graph.nodes]
    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init="auto")
    kmeans.fit(distances)
    return kmeans.labels_

def create_new_topology(graph, clusters, data_points):
    """
    Creates a new topology based on clusters only.
    No medoids are used.
    """
    # Create a dictionary to store cluster members
    cluster_members = {i: [] for i in range(max(clusters) + 1)}
    for i, node in enumerate(data_points):
        cluster_members[clusters[i]].append(node)

    # Build the new topology
    new_topology = {
        "directed": False,
        "multigraph": False,
        "graph": {},
        "nodes": [],
        "links": []
    }

    # Add nodes to the new topology
    for node in data_points:
        new_topology["nodes"].append({"id": node})

    # Add links based on clusters
    for cluster_id, members in cluster_members.items():
        for i, node1 in enumerate(members):
            for j, node2 in enumerate(members):
                if i < j:  # Add each edge only once
                    # Get latency from the original graph
                    latency = graph[node1][node2]['weight'] if graph.has_edge(node1, node2) else 0
                    # Add link only if latency is not 0
                    if latency != 0:
                        new_topology["links"].append({
                            "source": node1,
                            "target": node2,
                            "latency": latency
                        })

    return new_topology

def save_topology_to_json(topology, num_nodes, num_clusters):
    """Saves the topology to a JSON file with date and time in the filename."""
    # Create directory if it doesn't exist
    output_dir = "topology_kmeans"
    os.makedirs(output_dir, exist_ok=True)

    # Get current date and time
    now = datetime.now()
    dt_string = now.strftime("%b%d%Y%H%M")  # Format: Dec2320241946

    # Construct the full file path
    filename = f"kmeans_{num_nodes}Nodes_k{num_clusters}_{dt_string}.json"
    file_path = os.path.join(output_dir, filename)

    # Save the topology
    with open(file_path, 'w') as f:
        json.dump(topology, f, indent=4)


if __name__ == '__main__':

    # Step 1 - Get random topology file
    parser = argparse.ArgumentParser(description="Create K-means clustering.")
    parser.add_argument('--filename', required=True, help="Topology filename (Random gossip)")
    parser.add_argument('--num_cluster', required=True, help="Number of clusters to build")
    args = parser.parse_args()

    # Step 2 - Convert it to networkx (graph)
    prev_graph = get_prev_graph(args.filename)
    # print(f"prev_graph: {prev_graph}")

    # Step 3 - Contruct new clusters (using K-means)
    # num_clusters = 3
    num_clusters = int(args.num_cluster)
    clusters = cluster_nodes(prev_graph, num_clusters)
    print(f"Clusters : \n {clusters}")

    # Step 4 - Build new topology based on clusters
    data_points = list(prev_graph.nodes)
    num_nodes = len(data_points)
    new_topology = create_new_topology(prev_graph, clusters, data_points)  # Pass prev_graph here

    # Step 5 - Save the new topology to a JSON file
    save_topology_to_json(new_topology, num_nodes, num_clusters)

# def get_prev_graph(filename):
#     """Loads JSON data from a file and creates a NetworkX graph."""
#
#     # Get the current working directory
#     current_directory = os.getcwd()
#
#     # Construct the full path to the topology folder
#     topology_folder = os.path.join(current_directory, "topology")
#
#     # Load data from the JSON file
#     with open(os.path.join(topology_folder, filename), 'r') as f:
#         data = json.load(f)
#
#     # Build graph (existing topology)
#     graph = nx.Graph()
#     for node in data['nodes']:
#         graph.add_node(node['id'])
#     for link in data['links']:
#         graph.add_edge(link['source'], link['target'], weight=link['latency'])
#     return graph
#
# def cluster_nodes(graph, num_clusters):
#     """Clusters nodes using k-means on shortest path distances."""
#     distance_matrix = dict(nx.all_pairs_dijkstra_path_length(graph))
#     distances = [[distance_matrix[n1][n2] for n2 in graph.nodes] for n1 in graph.nodes]
#     kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init="auto")
#     kmeans.fit(distances)
#     return kmeans.labels_
#
# def create_new_topology(graph, clusters, data_points):
#     """
#     Creates a new topology based on clusters only.
#     No medoids are used.
#     """
#     # Create a dictionary to store cluster members
#     cluster_members = {i: [] for i in range(max(clusters) + 1)}
#     for i, node in enumerate(data_points):
#         cluster_members[clusters[i]].append(node)
#
#     # Build the new topology
#     new_topology = {
#         "directed": False,
#         "multigraph": False,
#         "graph": {},
#         "nodes": [],
#         "links": []
#     }
#
#     # Add nodes to the new topology
#     for node in data_points:
#         new_topology["nodes"].append({"id": node})
#
#     # Add links based on clusters
#     for cluster_id, members in cluster_members.items():
#         for i, node1 in enumerate(members):
#             for j, node2 in enumerate(members):
#                 if i < j:  # Add each edge only once
#                     # Get latency from the original graph
#                     latency = graph[node1][node2]['weight'] if graph.has_edge(node1, node2) else 0
#                     # Add link only if latency is not 0
#                     if latency != 0:
#                         new_topology["links"].append({
#                             "source": node1,
#                             "target": node2,
#                             "latency": latency
#                         })
#
#     return new_topology
#
# def save_topology_to_json(topology, num_nodes, num_clusters):
#     """Saves the topology to a JSON file with date and time in the filename."""
#     # Create directory if it doesn't exist
#     output_dir = "topology_kmeans"
#     os.makedirs(output_dir, exist_ok=True)
#
#     # Get current date and time
#     now = datetime.now()
#     dt_string = now.strftime("%b%d%Y%H%M")  # Format: Dec2320241946
#
#     # Construct the full file path
#     filename = f"kmeans_{num_nodes}Nodes_k{num_clusters}_{dt_string}.json"
#     file_path = os.path.join(output_dir, filename)
#
#     # Save the topology
#     with open(file_path, 'w') as f:
#         json.dump(topology, f, indent=4)