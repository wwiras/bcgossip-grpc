import networkx as nx
import random

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

            print(f"Highest degree node: {highest_degree_node}, with degree: {highest_degree}" )
            print(f"Lowest degree node: {lowest_degree_node}, with degree: {lowest_degree}")
            # break

            # Get neighbors of the highest degree node
            neighbors = list(graph.neighbors(highest_degree_node))

            # Randomly choose a neighbor to remove
            if neighbors:  # Check if there are any neighbors
                neighbor_to_remove = random.choice(neighbors)

                # Remove the edge to the chosen neighbor
                graph.remove_edge(highest_degree_node, neighbor_to_remove)
                print(f"Remove neighbor Node:{neighbor_to_remove} from  Node:{highest_degree_node}")

                print(f"Check if network graph connected? {nx.is_connected(graph)}")
                if not nx.is_connected(graph):
                    graph.add_edge(neighbor_to_remove,lowest_degree_node)
                    print(f"Add Node:{neighbor_to_remove} as Node:{lowest_degree_node}'s neighbor")

            avg_degree = round(sum(dict(graph.degree()).values()) / graph.number_of_nodes())
            print(f"Average degree: {avg_degree}, from {sum(dict(graph.degree()).values()) / graph.number_of_nodes()}")
            # break

        else:
            graph = False
            break

    return graph


# Parameters for the BA model
n = 150  # Number of nodes in the network
m = 2    # Number of edges to attach from a new node to existing nodes
target_avg_degree = m  # Target average degree

# Initial status
# Print some information about the graph
print(f"Initial status from the input .....")
print(f"Number of nodes in the network: {n}")
print(f"Average neighbor (degree): {m}")
# print(f"Target average degree: {target_avg_degree}")

# Create a BA model graph
print(f"Creating BARABASI ALBERT (BA) network model .....")
BA_graph = nx.barabasi_albert_graph(n, m)
print(f"Done! Below are the BA details")
print(f"Number of nodes: {BA_graph.number_of_nodes()}")
print(f"Number of edges: {BA_graph.number_of_edges()}")
print(f"Current BA is connected? True/False: {nx.is_connected(BA_graph)}")

# Check if average degree is as required
print(f"Check if average degree (neighbor) is as required: {m} ....")
current_avg_degree = sum(dict(BA_graph.degree()).values()) / n
print(f"Current average degree: {current_avg_degree}")
print(f"Target average degree: {m}")

if current_avg_degree > target_avg_degree:
    print(f"current_avg_degree:{current_avg_degree} is more than target_avg_degree: {m}")
    print(f"Fix graph average degree to target_avg_degree:{target_avg_degree}")
    BA_graph = fix_nodes_edge(BA_graph,m)

    if BA_graph:
        print(f"Graph fix is SUCCESSFUL ! : {BA_graph} ....")
    else:
        print(f"Graph fix is FAIL ! ....")

# Post-processing: Remove edges to reduce average degree
# BA_graph = remove_edges_from_high_degree_nodes(BA_graph, target_avg_degree)

# Print some information about the graph
# print(f"Number of nodes: {BA_graph.number_of_nodes()}")
# print(f"Target average degree: {target_avg_degree}")
# print(f"Number of edges: {BA_graph.number_of_edges()}")
# print(f"Average degree: {sum(dict(BA_graph.degree()).values()) / n}")
# print(f"Connected: {nx.is_connected(BA_graph)}")