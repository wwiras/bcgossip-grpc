import networkx as nx
from sklearn.cluster import KMeans
import random
import time
import matplotlib.pyplot as plt
import os
import json
import argparse

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
    kmeans = KMeans(n_clusters=int(num_clusters), random_state=0, n_init="auto")
    kmeans.fit(distances)
    return kmeans.labels_


def create_new_topology(graph, clusters, data_points):
    """Creates a new topology based on clusters and intra-cluster medoids."""
    # Create a dictionary to store cluster members
    cluster_members = {i: [] for i in range(max(clusters) + 1)}
    for i, node in enumerate(data_points):
        cluster_members[clusters[i]].append(node)

    # Find medoids for each cluster
    cluster_medoids = {}
    for cluster_id, members in cluster_members.items():
        if not members:
            continue

        # Filter the graph to include only nodes from the current cluster
        subgraph = graph.subgraph(members)

        # Find medoid based on shortest path within subgraph
        distance_matrix = dict(nx.all_pairs_dijkstra_path_length(subgraph))
        min_avg_distance = float('inf')
        medoid = None
        for node in members:
            total_distance = sum(distance_matrix[node].values())
            avg_distance = total_distance / len(members) if len(members) > 0 else 0
            if avg_distance < min_avg_distance:
                min_avg_distance = avg_distance
                medoid = node
        cluster_medoids[cluster_id] = medoid

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

    # Add links based on clusters and medoids
    for cluster_id, members in cluster_members.items():
        medoid = cluster_medoids[cluster_id]
        for node in members:
            if node != medoid:
                # Ensure the medoid is always the source for consistency
                source, target = (medoid, node) if node > medoid else (node, medoid)
                latency = graph[source][target]['weight'] if graph.has_edge(source, target) else 0
                new_topology["links"].append({
                    "source": source,
                    "target": target,
                    "latency": latency
                })

    return new_topology


def save_topology_to_json(topology, filename):
    """Saves the topology to a JSON file."""
    # Create directory if it doesn't exist
    output_dir = "topology_kmeans"
    os.makedirs(output_dir, exist_ok=True)

    # Construct the full file path
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

    # Step 3 - Construct new clusters (using K-means)
    num_clusters = int(args.num_cluster)
    clusters = cluster_nodes(prev_graph, num_clusters)
    print(f"Clusters: \n {clusters}")

    # Step 4 - Build new topology based on clusters
    data_points = list(prev_graph.nodes)
    new_topology = create_new_topology(prev_graph, clusters, data_points)

    # Step 5 - Save the new topology to a JSON file
    output_filename = f"k8s_gossip_kmeans_topology_{num_clusters}.json"
    save_topology_to_json(new_topology, output_filename)

    print(f"New topology saved to {output_filename}")