import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import combinations
import random
import os
from datetime import datetime
import argparse

def set_network_latency(graph,min_latency=1,max_latency=100):

    # Registered network graph with its neighbor
    # and its weight (latency)
    for u, v in combinations(graph, 2):
        if graph.has_edge(u, v) and 'weight' not in graph.edges[u, v]:
            graph.edges[u, v]['weight'] = random.randint(min_latency,max_latency)

    return graph

def set_network_mapping(graph,number_of_nodes):

    # Rename nodes
    mapping = {i: f"gossip-statefulset-{i}" for i in range(number_of_nodes)}
    network = nx.relabel_nodes(graph, mapping)

    return network

def fix_nodes_edge(graph, target_avg_degree):
    """Removes edges from nodes with degree higher than the target average degree.

    Args:
      graph: A NetworkX graph.
      target_avg_degree: The target average degree.

    Returns:
      The modified graph with reduced average degree.
    """

    avg_degree = round(sum(dict(graph.degree()).values()) / graph.number_of_nodes())
    print(f"Fix BA model initiating..." )
    print(f"Average degree started: {avg_degree}, from {sum(dict(graph.degree()).values()) / graph.number_of_nodes()}" )
    while avg_degree > target_avg_degree:

        if nx.is_connected(graph):

            # Get node degrees
            degrees = dict(graph.degree())

            # Highest degree node
            highest_degree_node = max(degrees, key=degrees.get)
            highest_degree = degrees[highest_degree_node]

            # Lowest degree node
            lowest_degree_node = min(degrees, key=degrees.get)
            lowest_degree = degrees[lowest_degree_node]

            # print(f"Highest degree node: {highest_degree_node}, with degree: {highest_degree}" )
            # print(f"Lowest degree node: {lowest_degree_node}, with degree: {lowest_degree}")
            # break

            # Get neighbors of the highest degree node
            neighbors = list(graph.neighbors(highest_degree_node))

            # Randomly choose a neighbor to remove
            if neighbors:  # Check if there are any neighbors
                neighbor_to_remove = random.choice(neighbors)

                # Remove the edge to the chosen neighbor
                graph.remove_edge(highest_degree_node, neighbor_to_remove)
                # print(f"Remove neighbor Node:{neighbor_to_remove} from  Node:{highest_degree_node}")

                # print(f"Check if network graph connected? {nx.is_connected(graph)}")
                if not nx.is_connected(graph):
                    graph.add_edge(neighbor_to_remove,lowest_degree_node)
                    # print(f"Add Node:{neighbor_to_remove} as Node:{lowest_degree_node}'s neighbor")

            avg_degree = round(sum(dict(graph.degree()).values()) / graph.number_of_nodes())
            # print(f"Average degree: {avg_degree}, from {sum(dict(graph.degree()).values()) / graph.number_of_nodes()}")
            # break

        else:
            graph = False
            break

    if graph:
        print(f"Average degree after: {avg_degree}, from {sum(dict(graph.degree()).values()) / graph.number_of_nodes()}")
    return graph

def construct_BA_network(number_of_nodes, parameter):

    # Initial status
    # Print some information about the graph
    # print(f"Initial status from the input .....")
    # print(f"Number of nodes in the network: {number_of_nodes}")
    # print(f"Average neighbor (degree): {parameter}")

    # Construct Barabási – Albert(BA) model topology
    # Create a BA model graph
    print(f"Creating BARABASI ALBERT (BA) network model .....")
    network = nx.barabasi_albert_graph(number_of_nodes, parameter)
    network.name = 'Barabási – Albert(BA)'
    # print(f"Number of nodes: {network.number_of_nodes()}")
    # print(f"Number of edges: {network.number_of_edges()}")
    # print(f"Current BA is connected? True/False: {nx.is_connected(network)}")

    # Check if average degree is as required
    # print(f"Check if average degree (neighbor) is as required: {parameter} ....")
    current_avg_degree = sum(dict(network.degree()).values()) / number_of_nodes
    # print(f"Current average degree: {current_avg_degree}")
    # print(f"Target average degree: {parameter}")

    if current_avg_degree > parameter:
        print(f"current_avg_degree:{current_avg_degree} is more than target_avg_degree: {parameter}")
        print(f"Fix graph average degree to target_avg_degree:{parameter}")
        BA_graph = fix_nodes_edge(network, parameter)

        if BA_graph:
            return network
        else:
            return False

def construct_ER_network(number_of_nodes, probability_of_edges):

    average_degree_raw = probability_of_edges * (number_of_nodes - 1)  # average_degree float
    average_degree = round(average_degree_raw)  # average_degree rounding

    print(f"Initial status from the input .....")
    print(f"Number of nodes in the network: {number_of_nodes}")
    print(f"Connection probability (degree): {probability_of_edges}")
    print(f"average_degree: {average_degree} with average_degree_raw: {average_degree_raw}")

    # Create an ER model graph
    ER_graph = nx.erdos_renyi_graph(number_of_nodes, probability_of_edges)
    print(f"Graph: {ER_graph}")
    avg_graph_degree_raw = sum(dict(ER_graph.degree()).values()) / number_of_nodes
    print(f"avg_graph_degree_raw: {avg_graph_degree_raw}")
    avg_graph_degree = round(avg_graph_degree_raw)
    print(f"avg_graph_degree: {avg_graph_degree}")

    if avg_graph_degree == average_degree:
        return ER_graph
    else:
        return False

def iterate_and_print_graph(graph):
    """Iterates over the graph and prints its content in a structured format."""

    print("\nGraph Data:")

    # Print general graph info
    # print("Name:", graph.name)
    print("Graph:", graph)
    # print(f"Average weight (in this case - latency): {calculate_average_weight(graph):.4f} ms")
    print(f"Average weight (in this case - latency): {graph.average_weight:.4f} ms")
    # print("Number of nodes:", graph.number_of_nodes())
    # print("Number of edges:", graph.number_of_edges())

    # Print node information
    # print("\nNodes:")
    # for node, data in graph.nodes(data=True):
    #     print(f"  - ID: {node}")
    #     # Access node attributes
    #     for key, value in data.items():
    #         print(f"    {key}: {value}")

    # Print edge information
    # print("\nEdges:")
    # for source, target, data in graph.edges(data=True):
    #     print(f"  - Source: {source}, Target: {target}")
    #     # Access edge attributes
    #     for key, value in data.items():
    #         print(f"    {key}: {value}")

def calculate_average_weight(graph):
    # Get all edge weights
    edge_weights = [data['weight'] for u, v, data in graph.edges(data=True)]

    # Calculate the average
    average_weight = sum(edge_weights) / len(edge_weights)

    return average_weight

def display_graph(graph, title="Network Graph"):
  """
  Displays a network graph using Matplotlib.

  Args:
    graph: The NetworkX graph object.
    title: (Optional) The title of the plot.
  """

  pos = nx.spring_layout(graph)  # Position nodes using spring layout

  # Draw nodes with labels
  nx.draw(graph, pos, with_labels=True, node_size=500, node_color="lightblue")

  # Draw edge labels (if any)
  edge_labels = nx.get_edge_attributes(graph, 'weight')
  if edge_labels:
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

  plt.title(title)
  plt.show()

def save_topology_to_json(graph, others, type="BA"):
    """
    Saves the network topology to a JSON file.

    Args:
    graph: The NetworkX graph object.
    filename: (Optional) The name of the JSON file to save.
    """

    # Get current date and time + second
    now = datetime.now()
    # dt_string = now.strftime("%b%d%Y%H%M")  # Format: Dec2320241946
    dt_string = now.strftime("%b%d%Y%H%M%S")  # Format: Dec232024194653
    filename = f"nodes{len(graph)}_{dt_string}_{type}{others}.json"

    # Create directory if it doesn't exist
    output_dir = "topology"
    os.makedirs(output_dir, exist_ok=True)

    # prepare topology in json format
    # Successfully installed networkx-3.4.2
    # Use "edges" for forward compatibility
    graph_data = nx.node_link_data(graph, edges="edges")
    graph_data["weight_average"] = graph.average_weight
    graph_data["total_edges"] = graph.total_edges
    graph_data["total_nodes"] = graph.total_nodes
    file_path = os.path.join(output_dir, filename)
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Topology saved to {filename}")

def confirm_save(graph,others,model):
    save_graph = input("Do you want to save the graph? (y/n): ")
    if save_graph.lower() == 'y':
        # Save the topology to a JSON file
        save_topology_to_json(graph, others, model)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send a message to self (the current pod).")
    parser.add_argument('--nodes', required=True, help="Total number of nodes for the topology")
    parser.add_argument('--others', required=True, help="Total number of probability (ER) or parameter (BA)")
    parser.add_argument('--model', required=True, help="Total number of nodes for the topology")
    # Add the optional argument with a default value of False
    parser.add_argument('--minlat', default=1 , help="Total number of nodes for the topology")
    parser.add_argument('--maxlat', default=100, help="Total number of nodes for the topology")
    parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
    parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
    args = parser.parse_args()

    # Getting minimum and maximum lateny
    minlat = int(args.minlat)
    maxlat = int(args.maxlat)

    if args.model== "BA":

        # Using BA Model
        number_of_nodes = int(args.nodes)
        parameter = int(args.others)
        graph = construct_BA_network(number_of_nodes, parameter)

    else:

        # Using ER Model
        number_of_nodes = int(args.nodes)
        probability_of_edges = float(args.others) # 0.5
        graph = construct_ER_network(number_of_nodes, probability_of_edges)

        # if args.save:
        # Save the topology to a JSON file
        #     save_topology_to_json(graph, probability_of_edges, "ER")

    if graph:

        print(f"Graph Before: {network}")

        # Set network mapping (gossip-statefulset labelling)
        network = set_network_mapping(graph, number_of_nodes)

        # Set latency ranging from minimum and maximum latency
        network = set_network_latency(network,minlat,maxlat)

        # Get average latency for the network
        network.average_weight = calculate_average_weight(network)

        # Get nodes and edge info
        network.total_edges = network.number_of_edges()
        network.total_nodes = network.number_of_nodes()

        # Asking to save it or not
        print(f"{args.model} network model is SUCCESSFUL ! ....")
        print(f"Graph After: {network}")
        if args.model == 'BA':
            confirm_save(network,parameter,args.model)
        else:
            confirm_save(network, probability_of_edges, args.model)

    else:
        print(f"{args.model} network model is FAIL ! ....")

    # Iterate and print the graph content
    # iterate_and_print_graph(graph)



# def construct_BA_network(number_of_nodes, parameter):
#
#     connected=False
#     # make sure all nodes are connected.
#     # if not connected, we will recreate the BA graph model
#     while connected==False:
#         # Construct Barabási – Albert(BA) model topology
#         network = nx.barabasi_albert_graph(number_of_nodes, parameter)
#         network.name = 'Barabási – Albert(BA)'
#
#         # Rename nodes
#         # mapping = {i: f"gossip-statefulset-{i + 1}" for i in range(number_of_nodes)}
#         mapping = {i: f"gossip-statefulset-{i}" for i in range(number_of_nodes)}
#         network = nx.relabel_nodes(network, mapping)
#
#         # Registered network graph with its neighbor
#         # and its weight (latency)
#         for u, v in combinations(network, 2):
#             if network.has_edge(u, v) and 'weight' not in network.edges[u, v]:
#                 network.edges[u, v]['weight'] = random.randint(1, 100)
#
#         # check if all nodes connected or not
#         if nx.is_connected(network):
#             connected=True
#
#     return network
#
# def construct_ER_network(number_of_nodes, probability_of_edges):
#
#     connected = False
#     # make sure all nodes are connected.
#     # if not connected, we will recreate the BA graph model
#     while connected == False:
#         network = nx.Graph()
#         network.name = 'Erdös – Rényi(ER)'
#
#         # Creating nodes
#         for i in range(number_of_nodes):
#             network.add_node(f"gossip-statefulset-{i}")
#
#         # Add node edges
#         for u, v in combinations(network, 2):
#             if random.random() < probability_of_edges:
#                 if u != v:
#                     network.add_edge(u, v, weight=random.randint(1, 100))
#
#         # check if all nodes connected or not
#         if nx.is_connected(network):
#             connected = True
#
#     return network


