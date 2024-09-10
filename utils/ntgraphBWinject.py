import json
import random
import argparse
import uuid
import os

def modify_topology(input_filename, bwidth=None):
    """
    Modifies an existing topology JSON file to set node bandwidths and saves it to a new file.

    Args:
        input_filename: The name of the input JSON file containing the network topology.
        bwidth: (Optional) The bandwidth to assign to all nodes (e.g., "1M").
                If not provided, random bandwidths will be assigned.
    """

    with open(input_filename, 'r') as f:
        topology = json.load(f)

    num_nodes = len(topology['nodes'])

    # Assign bandwidths to nodes
    if bwidth:
        for node in topology['nodes']:
            node['bandwidth'] = bwidth
    else:
        bandwidth_options = [1, 3, 5, 10]
        for node in topology['nodes']:
            node['bandwidth'] = str(random.choice(bandwidth_options))+"M"

    # Generate a 5-character UUID
    uuid_str = str(uuid.uuid4()).replace('-', '')[:5]

    # Extract base filename and strip the third underscore
    base_filename = os.path.splitext(os.path.basename(input_filename))[0]
    parts = base_filename.split('_')
    print(parts)
    if len(parts) >= 3:
        base_filename = '_'.join(parts[:3])  # Keep only the first three parts
    else:
        print("Warning: Input filename doesn't have the expected format. Using the original base filename.")

    # Create output filename
    if bwidth:
        output_filename = f'{base_filename}_{uuid_str}_{bwidth}.json'
    else:
        output_filename = f'{base_filename}_{uuid_str}_RM.json'
    print(output_filename)

    # Save the modified topology to the new file
    with open(output_filename, 'w') as f:
        json.dump(topology, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Modify an existing network topology JSON file to set node bandwidths and save it to a new file.')
    parser.add_argument('--input_filename', type=str, required=True, help='The name of the input JSON file containing the network topology.')
    parser.add_argument('--bwidth', type=str, help='Optional bandwidth for all nodes (e.g., "1M"). If not provided, random bandwidths will be assigned and the output filename will end with "_RM".')
    args = parser.parse_args()

    modify_topology(args.input_filename, args.bwidth)