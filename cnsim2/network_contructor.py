"""
This script is used to create network topology using ER model
"""
import networkx as nx
import json
import os
from datetime import datetime
import argparse

def set_network_mapping(graph,number_of_nodes):
    """
    Renaming nodes based on gossip-statefulset
    """

    # Rename nodes
    mapping = {i: f"gossip-statefulset-{i}" for i in range(number_of_nodes)}
    network = nx.relabel_nodes(graph, mapping)

    return network

def construct_ER_network(number_of_nodes, probability_of_edges):
    """
    Contruct ER model network topology
    Input:
    number_of_nodes: total of number of nodes in the ER network model
    probability_of_edges: probability value of edges in the ER network model in float between 0 and 1
    Output:
    graph object with ER network topology if all nodes are connected
    or
    False value indicates that ER network topology
    """

    # print(f"Initial status from the input .....")
    # print(f"Number of nodes in the network: {number_of_nodes}")
    # print(f"Connection probability (degree): {probability_of_edges}")

    # Create an ER model graph
    ER_graph = nx.erdos_renyi_graph(number_of_nodes, probability_of_edges)
    print(f"Graph: {ER_graph}")

    # Get the separate components
    components = list(nx.connected_components(ER_graph))
    # print(f"components: {components}")

    # If there's more than one component, connect them
    if len(components) > 1:
        return False
    else:
        return ER_graph

def save_topology_to_json(graph, prob):
    """
    Saves the network topology to a JSON file.

    Args:
    graph: The NetworkX graph object.
    filename: (Optional) The name of the JSON file to save.
    """

    # Get current date and time + second
    type = "ER"
    now = datetime.now()
    dt_string = now.strftime("%b%d%Y%H%M%S")  # Format: Dec232024194653
    filename = f"nodes{len(graph)}_{dt_string}_{type}{prob}.json"

    # Create directory if it doesn't exist
    output_dir = "topology"
    os.makedirs(output_dir, exist_ok=True)

    # prepare topology in json format
    graph_data = nx.node_link_data(graph, edges="edges")
    graph_data["total_edges"] = graph.total_edges
    graph_data["total_nodes"] = graph.total_nodes
    graph_data["model"] = type
    file_path = os.path.join(output_dir, filename)
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Topology saved to {filename}")

def confirm_save(graph,others):
    save_graph = input("Do you want to save the graph? (y/n): ")
    if save_graph.lower() == 'y':
        # Save the topology to a JSON file
        save_topology_to_json(graph, others)

if __name__ == '__main__':

    # Getting input to generate ER model network topology
    parser = argparse.ArgumentParser(description="Generate network topology using ER model")
    parser.add_argument('--nodes', required=True, help="Total number of nodes for the topology")
    parser.add_argument('--prob', required=True, help="Total number of probability (ER)")
    # Add the optional argument with a default value of False
    parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
    args = parser.parse_args()

    # Using ER Model
    number_of_nodes = int(args.nodes)
    probability_of_edges = float(args.prob) # 0.5
    graph = construct_ER_network(number_of_nodes, probability_of_edges)

    # Set network mapping
    # print(f"graph: {graph}")
    if graph:
        # Remapping graph network
        network = set_network_mapping(graph, number_of_nodes)

        # Get nodes and edge info
        network.total_edges = network.number_of_edges()
        network.total_nodes = network.number_of_nodes()

        # Confirmation on creating json (topology) file
        # print(f"Graph: {network}")
        confirm_save(network, probability_of_edges)
        print(f"ER network model is SUCCESSFUL ! ....")
    else:
        print(f"ER network model is FAIL ! ....")
