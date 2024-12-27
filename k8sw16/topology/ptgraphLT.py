import json
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def visualize_graph(json_data):
  """
  Visualizes a graph from a JSON object with latency information.

  Args:
    json_data: A JSON object containing graph data with 'nodes' and 'edges' (including 'weight').
  """

  graph = nx.Graph()
  graph.add_nodes_from(json_data['nodes'])

  for edge in json_data['edges']:
    graph.add_edge(edge['source'], edge['target'], weight=edge['weight'])

  # Position nodes using spring layout
  pos = nx.spring_layout(graph)

  # Draw the graph
  nx.draw(graph, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=8)

  # Add edge labels for latency
  labels = nx.get_edge_attributes(graph, 'weight')
  nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

  plt.title("Graph Visualization with Latency")
  plt.show()

if __name__ == '__main__':
  # Parse command-line arguments
  parser = argparse.ArgumentParser(description='Visualize a network graph from a JSON file.')
  parser.add_argument('--filename', type=str, required=True, help='The name of the JSON file containing the network topology.')
  args = parser.parse_args()

  # Load the JSON data from the specified file
  with open(args.filename, 'r') as f:
    json_data = json.load(f)

  # Visualize the graph
  visualize_graph(json_data)