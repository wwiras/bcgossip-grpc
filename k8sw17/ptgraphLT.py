import networkx as nx
import matplotlib.pyplot as plt
import json
import argparse

def display_graph_from_json(filename):
    """
    Displays a graph with edge weights from a JSON file.

    Args:
        filename: The path to the JSON file containing the graph data.
    """

    with open(filename, 'r') as f:
        data = json.load(f)

    graph = nx.Graph()
    for node in data['nodes']:
        graph.add_node(node['id'])
    for edge in data['edges']:  # Use 'edges' instead of 'links'
        graph.add_edge(edge['source'], edge['target'], weight=edge['weight'])

    pos = nx.spring_layout(graph)  # You can choose a different layout if you prefer
    nx.draw(graph, pos, with_labels=True)

    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    plt.show()

if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Visualize a network graph from a JSON file.')
  parser.add_argument('--filename', type=str, required=True, help='The name of the JSON file containing the network topology.')
  args = parser.parse_args()


  # Visualize the graph
  display_graph_from_json(args.filename)