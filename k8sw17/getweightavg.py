import json
import os
import networkx as nx

def calculate_weighted_average(graph):
    """Calculates weighted average of edges in a NetworkX graph."""
    if not graph.edges:
        return 0

    total_weight = sum(data.get("weight", 0) for u, v, data in graph.edges(data=True))
    num_edges = graph.number_of_edges()
    return total_weight / num_edges if num_edges > 0 else 0

def process_json_file(file_path):
    """Processes a single JSON file, adding to NetworkX graph and updating."""

    print(f"Processing file: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return

    # Determine graph type
    # if data.get('directed', False):
    #     graph = nx.DiGraph()
    # else:
    #     graph = nx.Graph()

    graph = nx.Graph()
    print(f"Graph loaded: {graph}")
    # print(f"data: {data}")
    print(f"len(data['nodes']): {len(data['nodes'])}")
    print(f"len(data['edges']): {len(data['edges'])}")

    print(f"Adding nodes from {file_path}...")
    for node_data in data.get("nodes",):
        try:
            graph.add_node(node_data["id"], **node_data)
        except Exception as e:
            print(f"Error adding node {node_data.get('id', 'N/A')} from {file_path}: {e}")
            return  # Stop processing if node error
    print(f"Graph nodes loaded: {graph}")


    for edge_data in data["edges"]:
        # print(f"edge_data:{edge_data}...")
        graph.add_edge(edge_data["source"], edge_data["target"], weight=edge_data["weight"])
    print(f"Graph nodes and edges loaded: {graph}")

    weighted_average = calculate_weighted_average(graph)
    print(f"weighted_average : {weighted_average }")

    # Include 'directed', 'multigraph', and 'graph'

    # graph.graph['directed'] = False
    # graph.graph['multigraph']= False
    # graph.graph['total_clusters'] = data['total_clusters']
    # graph.graph['total_nodes'] = len(data['nodes'])
    # graph.graph['total_edges'] = len(data['edges'])
    # graph.graph['weight_average'] = weighted_average
    # # Add clustering time as a comment (disabled by default)
    # graph.graph['total_clustering_time_ms'] = data['total_clustering_time_ms']
    # graph.graph['graph'] = {}
    # print(f"graph.graph={graph.graph}")

    graph_data = {
        'directed': False,
        'multigraph': False,
        'total_clusters': data['total_clusters'],
        'total_nodes': len(data['nodes']),
        'total_edges': len(data['edges']),
        'weight_average': weighted_average,
        # Add clustering time as a comment (disabled by default)
        'total_clustering_time_ms': data['total_clustering_time_ms'],
        'graph': {},
        'nodes': data['nodes'],
        'edges': data['edges']
    }
    # print(f"graph_data{graph_data}")

    # print(f"Saving updated JSON to {file_path}...")
    try:
        with open(file_path, 'w') as f:
            json.dump(graph_data, f, indent=4)
        return True
    except Exception as e:
        print(f"error writing graph to file: {file_path}: {e}")
        return False

    # print(f"Finished processing: {file_path}")

def process_directory(directory_path):
    """Processes all JSON files in a directory."""
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return

    print(f"Processing directory: {directory_path}")

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            process_json_file(file_path)

    print(f"Finished processing directory: {directory_path}")

# Example usage:
current_directory = os.getcwd()
topology_folder = os.path.join(current_directory, "topology_kmeans")

# ICCMS2025
# filename = "kmeans_nodes10_Feb072025182408_ER0.5_k3.json"
# filename = "kmeans_nodes10_Feb072025182500_BA3_k3.json"
# filename = "nodes50_Feb062025151733_BA2.json"
# filename = "nodes50_Feb062025152856_ER0.07.json"
# filename = "nodes150_Feb072025182958_ER0.02.json"
# filename = "nodes150_Feb072025183130_BA2.json"
# filename = "nodes100_Feb092025135238_BA2.json"
# filename = "nodes100_Feb092025135330_ER0.02.json"
# filename = "nodes300_Feb062025152130_BA2.json"
# filename = "nodes300_Feb072025183339_ER0.015.json"
# filename = "nodes300_Feb092025140244_ER0.02.json"
# filename = "nodes300_Feb092025140642_BA2.json"
# filename = "nodes300_Feb092025184433_ER0.015.json"
# filename = "nodes300_Feb092025185345_ER0.015.json"
# filename = "nodes50_Feb092025192653_ER0.07.json"
# filename = "nodes150_Feb092025194826_ER0.02.json"
# filename = "nodes300_Feb092025212956_ER0.015.json"

# file_path = os.path.join(topology_folder, filename)
# result = process_json_file(file_path)
# if result:
#     print("Finished processing")
# else:
#     print("Error: file not updated")

# Or process all files in the directory:
process_directory(topology_folder)
