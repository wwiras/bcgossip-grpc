from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
import time
import json
import logging
import os
import argparse
import grpc
import gossip_pb2
import gossip_pb2_grpc

# Configure logging
logging.basicConfig(filename='gossip_simulation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def shorten_node_name(node_name):
    """Shortens a Kubernetes-style node name (e.g., "gossip-statefulset-0")
    to a more concise format (e.g., "gs0").

    Args:
        node_name: The original node name.

    Returns:
        The shortened node name.
    """
    parts = node_name.split('-')
    return f"{parts[0][0]}{parts[1][0]}{parts[2]}"

def create_mininet_network(topology):
    """
    Creates a Mininet network based on the provided topology.
    """
    net = Mininet(controller=Controller)
    net.addController('c0')

    # Add hosts (nodes) based on the topology
    hosts = {}
    for node in topology['nodes']:
        host_name_long = node['id']  # Assuming 'id' is the host name in your JSON
        host_name = shorten_node_name(host_name_long)
        hosts[host_name] = net.addHost(host_name)

    # Add links with bandwidth and latency based on the topology
    for link in topology['edges']:
        source_long = link['source']
        source = shorten_node_name(source_long)
        target_long = link['target']
        target = shorten_node_name(target_long)
        latency = link['weight']  # Use 'weight' as latency
        net.addLink(source, target, cls=TCLink, delay=f"{latency}ms")  # Add link with latency

    net.start()
    return net

def send_grpc_message(target_ip, message, sender_id):
    """
    Sends a message to a target node using gRPC.
    """
    target = f"{target_ip}:5050"
    with grpc.insecure_channel(target) as channel:
        stub = gossip_pb2_grpc.GossipServiceStub(channel)
        print(f"Sending message to {target_ip}: '{message}'", flush=True)
        response = stub.SendMessage(gossip_pb2.GossipMessage(
            message=message,
            sender_id=sender_id,
            timestamp=time.time_ns(),
            latency_ms=0.00  # Latency is simulated in the link
        ))
        print(f"Received acknowledgment: {response.details}", flush=True)

def run_gossip_simulation(net, topology):
    """
    Runs a basic gossip simulation on the Mininet network using gRPC.
    """
    hosts = {shorten_node_name(node['id']): net.get(shorten_node_name(node['id'])) for node in topology['nodes']}  # Get host objects
    print(f"hosts: {hosts}")

    # Choose an initial sender (you can modify this)
    initial_sender_long = 'gossip-statefulset-0'  # Replace with the actual name of your initial sender
    initial_sender = shorten_node_name(initial_sender_long)

    # Send the initial message using gRPC
    message = "Hello from Mininet!"
    start_time = time.time_ns()
    send_grpc_message(hosts[initial_sender].IP(), message, initial_sender)

    # Wait for the message to propagate (you might need to adjust the timeout)
    time.sleep(5)

    # Collect propagation times (implementation depends on your gossip logic)
    # For this example, we'll just print the time when each host received the message
    # for host_name, host in hosts.items():
    #     if host_name != initial_sender:
    #         output = host.cmd('cat /tmp/received_message.txt')  # Assuming you're writing the received message to a file
    #         if output:
    #             received_time = float(output.splitlines()[-1].split()[-1])  # Extract the timestamp from the output
    #             propagation_time = (received_time - start_time) / 1e6  # in milliseconds
    #             logging.info(f"Propagation time to {host_name}: {propagation_time:.2f} ms")  # Log the propagation time

def get_topology(nodes, cluster, model, topology_folder):
    """
    Retrieves the topology file from the specified folder based on the number of nodes and model.
    """
    # Get the current directory
    current_directory = os.getcwd()
    print(f"Current directory: {current_directory}")

    # Move up one level
    parent_directory = os.path.dirname(current_directory)
    print(f"Parent directory: {parent_directory}")

    # Join the parent directory with the topology_folder
    topology_dir = os.path.join(parent_directory, topology_folder)
    print(f"Topology directory: {topology_dir}")

    # Construct the search string based on the cluster and model
    search_str = f'nodes{nodes}_' if cluster == '0' else f'kmeans_nodes{nodes}_'

    # Find the corresponding topology file
    topology_file = None
    for topology_filename in os.listdir(topology_dir):
        if topology_filename.startswith(search_str) and model in topology_filename:
            topology_file = topology_filename
            break

    if topology_file:
        with open(os.path.join(topology_dir, topology_file), 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"No topology file found for {nodes} nodes and model {model}.")

if __name__ == '__main__':
    # Get all args: cluster type, model, and total nodes
    parser = argparse.ArgumentParser(description="Run a gossip on Mininet.")
    parser.add_argument('--cluster', required=True, choices=['0', '1'], help="Cluster type: 0 for non-clustered, 1 for k-means clustered")
    parser.add_argument('--model', required=True, choices=['BA', 'ER'], help="Topology model: BA or ER")
    parser.add_argument('--nodes', required=True, type=int, help="Total number of nodes in the topology")
    args = parser.parse_args()

    # Determine the topology folder based on cluster type
    topology_folder = "topology" if args.cluster == '0' else "topology_kmeans"

    # Get topology file based on input
    topology = get_topology(args.nodes, args.cluster, args.model, topology_folder)

    # Create and start the Mininet network
    net = create_mininet_network(topology)

    # Run the gossip simulation
    run_gossip_simulation(net, topology)

    # Stop the network
    net.stop()