import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import combinations
import random
import os

def construct_BA_network(number_of_nodes, parameter):
    # Construct Barabási – Albert(BA) model topology
    network = nx.barabasi_albert_graph(number_of_nodes, parameter)
    network.name = 'Barabási – Albert(BA)'

    # Rename nodes
    mapping = {i: f"gossip-statefulset-{i + 1}" for i in range(number_of_nodes)}
    network = nx.relabel_nodes(network, mapping)

    # Registered network graph with its neighbor
    # and its weight (latency)
    for u, v in combinations(network, 2):
        if network.has_edge(u, v) and 'weight' not in network.edges[u, v]:
            network.edges[u, v]['weight'] = random.randint(1, 100)
            # network.nodes[u]['registered_neighbors'][v] = network.edges[u, v]['weight']
            # network.nodes[v]['registered_neighbors'][u] = network.edges[u, v]['weight']
    return network

# def construct_ER_network(number_of_nodes, probability_of_edges):
#     network = nx.Graph()
#     network.name = 'Erdös – Rényi(ER)'
#     for i in range(number_of_nodes):
#         network.add_node(i)
#         network.nodes[i]['registered_neighbors'] = {}
#         # network.nodes[i]['ONS'] = {}
#         # network.nodes[i]['received_msgs'] = Queue()
#         # network.nodes[i]['alive'] = True
#         # network.nodes[i]['MST'] = []
#     for u, v in combinations(network, 2):
#         if random.random() < probability_of_edges:
#             if u != v:
#                 network.add_edge(u, v, weight=random.randint(1, 100))
#                 network.nodes[u]['registered_neighbors'][v] = network.edges[u, v]['weight']
#                 network.nodes[v]['registered_neighbors'][u] = network.edges[u, v]['weight']
#     # get_network_ready(network)  # Make sure this function is defined if you need it
#     return network

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

def save_topology_to_json(graph, filename="network_topology.json"):
  """
  Saves the network topology to a JSON file.

  Args:
    graph: The NetworkX graph object.
    filename: (Optional) The name of the JSON file to save.
  """

  # Create directory if it doesn't exist
  output_dir = "temporary"
  os.makedirs(output_dir, exist_ok=True)

  graph_data = nx.node_link_data(graph, edges="edges")  # Use "edges" for forward compatibility
  file_path = os.path.join(output_dir, filename)
  with open(file_path, 'w') as f:
    json.dump(graph_data, f, indent=4)
  print(f"Topology saved to {filename}")


# Using BA Model
number_of_nodes = 8
parameter = 3
graph = construct_BA_network(number_of_nodes, parameter)
print(f"ba graph = {graph}")


# Using BE Model
# number_of_nodes = 8
# probability_of_edges = 0.5
# graph = construct_ER_network(number_of_nodes, probability_of_edges)
# print(f"er_graph = {graph}")


# Assuming you have a graph called 'ba_graph' (as in your previous code)
# display_graph(graph, "Barabási–Albert Network")
# display_graph(graph, "Erdös – Rényi(ER) Network")

# Save the topology to a JSON file
# save_topology_to_json(graph, "ba_topology.json")
# save_topology_to_json(graph, "er_topology.json")

# Iterate and print the graph content
iterate_and_print_graph(graph)



