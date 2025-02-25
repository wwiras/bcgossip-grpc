import networkx as nx
import random

def get_low_degree_nodes(graph, avg_degree):
    """Returns a list of nodes with degree less than the average degree.

    Args:
      graph: A NetworkX graph.
      avg_degree: The average degree requirement.

    Returns:
      A list of nodes with degree less than avg_degree.
    """
    low_degree_nodes = [node for node, degree in graph.degree() if degree < avg_degree]
    return low_degree_nodes

def connect_low_degree_nodes(graph, avg_degree):
    """Connects nodes with degree less than the average degree to other similar nodes.

    Args:
      graph: A NetworkX graph.
      avg_degree: The average degree requirement.

    Returns:
      The modified graph with low-degree nodes connected.
    """

    low_degree_nodes = get_low_degree_nodes(graph, avg_degree)

    # Shuffle the list to ensure random connections
    random.shuffle(low_degree_nodes)

    # Connect low-degree nodes in pairs
    for i in range(0, len(low_degree_nodes) - 1, 2):
        graph.add_edge(low_degree_nodes[i], low_degree_nodes[i + 1])

    # If there's an odd number, connect the last one to a random low-degree node
    if len(low_degree_nodes) % 2!= 0:
        last_node = low_degree_nodes[-1]
        random_node = random.choice(low_degree_nodes[:-1])  # Exclude the last node itself
        graph.add_edge(last_node, random_node)

    return graph

def ensure_connected(graph, avg_degree):
    """Ensures all nodes in the graph are connected and meet the average degree requirement.

    Args:
      graph: A NetworkX graph.
      avg_degree: The average degree requirement.

    Returns:
      The modified graph with all nodes connected and meeting the degree requirement.
    """

    while not nx.is_connected(graph):
        graph = connect_low_degree_nodes(graph, avg_degree)
    return graph


# Parameters for the ER model
n = 150  # Number of nodes in the network
# p = 0.1 # Connection probability (degree)
p = 0.02 # Connection probability (degree)
average_degree_raw = p * (n-1) # average_degree
average_degree = round(average_degree_raw)
print(f"Initial status from the input .....")
print(f"Number of nodes in the network: {n}")
print(f"Connection probability (degree): {p}")
print(f"average_degree: {average_degree} with average_degree_raw: {average_degree_raw}")

# Create an ER model graph
ER_graph = nx.erdos_renyi_graph(n, p)
print(f"Graph: {ER_graph}")
avg_graph_degree_raw = sum(dict(ER_graph.degree()).values())/n
print(f"avg_graph_degree_raw: {avg_graph_degree_raw}")
avg_graph_degree = round(avg_graph_degree_raw)
print(f"avg_graph_degree: {avg_graph_degree}")

if avg_graph_degree == average_degree:
    print(f"Graph ER is SUCCESSFUL ! : {ER_graph} ....")
else:
    print(f"Graph ER is FAIL ! : {ER_graph} ....")


# average_degree = 3  # Desired average degree

# Calculate the connection probability
# p = average_degree / (n - 1)


# average_degree = round(p * (n-1))
# test_avg = round(3.6)
# test_avg_raw = p * (n-1)


# Print some information about the graph
# print(f"Number of nodes: {ER_graph.number_of_nodes()}")
# print(f"Average degree required: {average_degree}")
# print(f"Number of edges: {ER_graph.number_of_edges()}")
# print(f"Average degree: {sum(dict(ER_graph.degree()).values()) / n}")
# print(f"Calculated connection probability: {p}")
# print(f"Connected: {nx.is_connected(ER_graph)}")
# print(f"test_avg: {test_avg}")
# print(f"test_avg: {test_avg_raw}")