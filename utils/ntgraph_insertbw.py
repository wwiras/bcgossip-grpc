import networkx as nx
import json
import random
import argparse

def add_bandwidth(topology_data, bandwidth_mbps=None):
    """
    Adds bandwidth values to the edges of a network topology.

    Args:
        topology_data: A dictionary representing the network topology in node-link format.
        bandwidth_mbps: (Optional) If provided, all edges will have this bandwidth in Mbps.
                        If None, edges will have random bandwidth from bandwidth_options.

    Returns:
        The modified topology data with bandwidth assigned to each edge.
    """
    G = nx.node_link_graph(topology_data)

    bandwidth_options = [1, 3, 5, 10]  # Mbps

    for u, v in G.edges():
        if bandwidth_mbps is None:
            G.edges[u, v]['bandwidth'] = random.choice(bandwidth_options)
        else:
            G.edges[u, v]['bandwidth'] = bandwidth_mbps

    return nx.node_link_data(G)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add bandwidth to a network topology JSON file.')
    parser.add_argument('--input_file', type=str, help='The input JSON file containing the network topology.')
    parser.add_argument('--bandwidth', type=int, help='(Optional) Constant bandwidth for all edges (in Mbps).')
    args = parser.parse_args()

    # Load the topology from the input file (use args.input_file)
    with open(args.input_file, 'r') as f:
        topology_data = json.load(f)

    # Add bandwidth to the topology (random or constant based on argument)
    modified_topology = add_bandwidth(topology_data, args.bandwidth)

    # Create the output filename (replace .json with _RM.json or _<bandwidth>M.json)
    bandwidth_type = f"{args.bandwidth}M" if args.bandwidth else "RM"
    output_filename = args.input_file.replace('.json', f'_{bandwidth_type}.json')

    # Save the modified topology to the output file
    with open(output_filename, 'w') as f:
        json.dump(modified_topology, f, indent=2)

    # print(f"Modified topology with bandwidth saved to {output_filename}")