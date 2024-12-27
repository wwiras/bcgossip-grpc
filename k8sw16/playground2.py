import networkx as nx
import json
import random
import argparse
import os
from datetime import datetime

def create_complete_graph(n, median_latency=10):
  """
  Creates a complete graph with n nodes, where each node is connected to every other node.
  Edges have random weights representing latency with a specified median.

  Args:
    n: The number of nodes in the graph.
    median_latency: The median latency for the edge weights.

  Returns:
    A NetworkX graph object and a JSON string representing the graph data.
  """

  graph = nx.complete_graph(n)
  num_edges = graph.number_of_edges()

  # Calculate the number of edges that should have latency below and above the median
  below_median = num_edges // 2
  above_median = num_edges - below_median

  # Generate latencies with a more controlled median
  latencies = (
      [random.randint(2, median_latency - 1) for _ in range(below_median)]  # Below median
      + [random.randint(median_latency, 100) for _ in range(above_median)]  # Above median
  )
  random.shuffle(latencies)  # Shuffle to distribute the latencies randomly

  # Add the latencies as edge weights
  for i, (u, v) in enumerate(graph.edges()):
    graph[u][v]['weight'] = latencies[i]

  # Calculate the degree of each node (which should be n-1)
  d = n - 1

  # Calculate the total number of edges
  total_edges = n * (n - 1) // 2

  # Prepare data for JSON output
  # nodes = [{'id': node} for node in graph.nodes]
  nodes = ['gossip-statefulset-' + str(i) for i in range(n)]
  edges = [{'source': 'gossip-statefulset-'+ str(u), 'target': 'gossip-statefulset-'+ str(v), 'weight': graph[u][v]['weight']} for u, v in graph.edges]
  graph_data = {
      "directed": False,
      "multigraph": False,
      "graph": {},
      "nodes": nodes,
      "edges": edges,
      "degree": d,
      "total_edges": total_edges
  }

  # Convert graph data to JSON string
  json_output = json.dumps(graph_data, indent=4)

  return graph, json_output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send a message to self (the current pod).")
    parser.add_argument('--nodes', required=True, help="Total number of nodes for the topology")
    args = parser.parse_args()

    # Create the graph and get the JSON output
    graph, json_output = create_complete_graph(int(args.nodes))

    # Get current date and time
    now = datetime.now()
    dt_string = now.strftime("%b%d%Y%H%M")  # Format: Dec2320241946

    # Construct the full file path
    output_dir = 'topology'
    filename = f"nt_nodes{int(args.nodes)}_{dt_string}.json"
    file_path = os.path.join(output_dir, filename)

    # Specify the directory to save the JSON file (current directory)
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    filename = os.path.join(output_dir, filename)

    # Print the JSON output
    print(json_output)

    # Save the JSON output to a file
    # with open(filename, 'w') as f:
    #     f.write(json_output)
        # json.dump(graph_data, filename, indent=4)

    # print(f"Topology saved to {filename}")