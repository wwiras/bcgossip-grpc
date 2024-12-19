import json, os

def get_total_nodes(filepath):
    """
    Extracts the total number of nodes from a JSON file.
    Args:
      filepath: The path to the JSON file.
    Returns:
      The total number of nodes in the network.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return len(data['nodes'])

def get_set_of_nodes(filepath):
    """
    Extracts the set of nodes from a JSON file.
    Args:
      filepath: The path to the JSON file.
    Returns:
      A set of node IDs in the network.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return {node['id'] for node in data['nodes']}

# Example usage
# Construct the full file path
filepath = os.path.join('topology', 'nt_nodes10_RM.json')
# filepath = 'nt_nodes10_RM.json'  # Replace with the actual path to your JSON file
total_nodes = get_total_nodes(filepath)
print(f"Total number of nodes: {total_nodes}")  # Output: 10

set_of_nodes = get_set_of_nodes(filepath)
print(f"Set of nodes: {set_of_nodes}")