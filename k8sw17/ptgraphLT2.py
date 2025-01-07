import networkx as nx
import matplotlib.pyplot as plt
import json
import argparse

def display_graph_from_json(filename):
    """
    Displays a graph with edge weights and colored nodes based on clusters
    from a JSON file, handling cases with or without cluster information.

    Args:
        filename: The path to the JSON file containing the graph data.
    """

    with open(filename, 'r') as f:
        data = json.load(f)

    graph = nx.Graph()
    for node in data['nodes']:
        graph.add_node(node['id'])
    for edge in data['edges']:
        graph.add_edge(edge['source'], edge['target'], weight=edge['weight'])

    # Check if cluster information exists
    if 'cluster' in data['nodes'][0]:
        node_to_cluster = {node['id']: node['cluster'] for node in data['nodes']}
        clusters = [node_to_cluster[node] for node in graph.nodes()]
    else:
        clusters = 0  # Assign a default color if no cluster information

    # Visualization
    pos = nx.spring_layout(graph)
    if clusters == 0:
        nx.draw(graph, pos, with_labels=True)
    else:
        nx.draw(graph, pos, with_labels=True, node_color=clusters, cmap=plt.cm.viridis)

    # Display edge weights
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    plt.show()

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Visualize a network graph from a JSON file.')
    parser.add_argument('--filename', type=str, required=True,
                        help='The name of the JSON file containing the network topology.')
    args = parser.parse_args()

    # Visualize the graph
    display_graph_from_json(args.filename)