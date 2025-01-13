import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import combinations
import random
import os
from datetime import datetime
import argparse

def construct_BA_network(number_of_nodes, parameter):

    connected=False
    # make sure all nodes are connected.
    # if not connected, we will recreate the BA graph model
    while connected==False:
        # Construct Barabási – Albert(BA) model topology
        network = nx.barabasi_albert_graph(number_of_nodes, parameter)
        network.name = 'Barabási – Albert(BA)'

        # Rename nodes
        # mapping = {i: f"gossip-statefulset-{i + 1}" for i in range(number_of_nodes)}
        mapping = {i: f"gossip-statefulset-{i}" for i in range(number_of_nodes)}
        network = nx.relabel_nodes(network, mapping)

        # Registered network graph with its neighbor
        # and its weight (latency)
        for u, v in combinations(network, 2):
            if network.has_edge(u, v) and 'weight' not in network.edges[u, v]:
                network.edges[u, v]['weight'] = random.randint(1, 100)

        # check if all nodes connected or not
        if nx.is_connected(network):
            connected=True

    return network

def construct_ER_network(number_of_nodes, probability_of_edges):

    connected = False
    # print(f'connected: {connected}')
    # make sure all nodes are connected.
    # if not connected, we will recreate the BA graph model
    while connected == False:
        network = nx.Graph()
        network.name = 'Erdös – Rényi(ER)'

        # Creating nodes
        for i in range(number_of_nodes):
            network.add_node(f"gossip-statefulset-{i}")
        # print(f'network: {network}')

        # Add node edges
        for u, v in combinations(network, 2):
            if random.random() < probability_of_edges:
                if u != v:
                    # network.add_edge(u, v, weight=random.randint(1, 100))
                    network.add_edge(u, v, weight=random.randint(1, 5))
        # print(f'network with edges: {network}')

        # check if all nodes connected or not
        # print(f'nx.is_connected(network): {nx.is_connected(network)}')
        if nx.is_connected(network):
            connected = True

    return network

def iterate_and_print_graph(graph):
    """Iterates over the graph and prints its content in a structured format."""

    print("\nGraph Data:")

    # Print general graph info
    print("Name:", graph.name)
    print("Type:", type(graph))
    print("Number of nodes:", graph.number_of_nodes())
    print("Number of edges:", graph.number_of_edges())

    # Print node information
    print("\nNodes:")
    for node, data in graph.nodes(data=True):
        print(f"  - ID: {node}")
        # Access node attributes
        for key, value in data.items():
            print(f"    {key}: {value}")

    # Print edge information
    print("\nEdges:")
    for source, target, data in graph.edges(data=True):
        print(f"  - Source: {source}, Target: {target}")
        # Access edge attributes
        for key, value in data.items():
            print(f"    {key}: {value}")

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
    file_path = os.path.join(output_dir, filename)
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, indent=4)
    print(f"Topology saved to {filename}")

def simulate_message_exchange(graph):
    """Simulates message exchange and calculates total propagation time."""
    total_messages = 0
    total_time = 0  # Initialize total time

    for u, v in graph.edges():
        # Example: Each node sends a message to each of its neighbors (excluding the current one)
        neighbors_u = list(graph.neighbors(u))
        neighbors_u.remove(v)
        total_messages += len(neighbors_u)  # Messages sent by u

        neighbors_v = list(graph.neighbors(v))
        neighbors_v.remove(u)
        total_messages += len(neighbors_v)  # Messages sent by v

        # Get the latency (weight) of the edge
        latency = graph[u][v]['weight']

        # Add latency to the total time for each message sent
        total_time += latency * (len(neighbors_u) + len(neighbors_v))

    return total_messages, total_time

if __name__ == '__main__':

    # number_of_nodes = 50  # Fixed number of nodes
    number_of_nodes = 1000  # Fixed number of nodes
    probability_of_edges = 0.1  # Fixed probability
    target_messages_min = 350
    target_messages_max = 400

    # while True:  # Keep generating networks until a suitable one is found
    er_graph = construct_ER_network(number_of_nodes, probability_of_edges)
    total_messages, total_time = simulate_message_exchange(er_graph)  # Get total_time

    print(f"Erdös-Rényi network with {number_of_nodes} nodes and probability {probability_of_edges:.2f}")
    print(f"Number of nodes: {er_graph.number_of_nodes()}")
    print(f"Number of edges: {er_graph.number_of_edges()}")
    print(f"Total messages exchanged: {total_messages}")
    print(f"Total propagation time: {total_time}")


    # parser = argparse.ArgumentParser(description="Send a message to self (the current pod).")
    # parser.add_argument('--nodes', required=True, help="Total number of nodes for the topology")
    # parser.add_argument('--others', required=True, help="Total number of probability (ER) or parameter (BA)")
    # parser.add_argument('--model', required=True, help="Total number of nodes for the topology")
    # # Add the optional argument with a default value of False
    # parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
    # parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
    # args = parser.parse_args()
    #
    #
    # if args.model== "BA":
    #
    #     # Using BA Model
    #     number_of_nodes = int(args.nodes)
    #     parameter = int(args.others)
    #     graph = construct_BA_network(number_of_nodes, parameter)
    #
    #     # Assuming you have a graph called 'ba_graph' (as in your previous code)
    #     if args.display:
    #         display_graph(graph, "Barabási–Albert Network")
    #
    #     if args.save:
    #         # Save the topology to a JSON file
    #         save_topology_to_json(graph,parameter)
    #
    # else:
    #
    #     # Using ER Model
    #     number_of_nodes = int(args.nodes)
    #     probability_of_edges = float(args.others) # 0.5
    #     graph = construct_ER_network(number_of_nodes, probability_of_edges)
    #
    #     if args.display:
    #         display_graph(graph, "Erdös – Rényi(ER) Network")
    #
    #     if args.save:
    #     # Save the topology to a JSON file
    #         save_topology_to_json(graph, probability_of_edges, "ER")

    # Iterate and print the graph content
    # iterate_and_print_graph(graph)




