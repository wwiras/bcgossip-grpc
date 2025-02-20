from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
import time
import json
import logging
import os
import argparse
import socket
import threading

# Configure logging
logging.basicConfig(filename='logs/gossip_simulation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def shorten_node_name(node_name):
    """Shortens a Kubernetes-style node name (e.g., "gossip-statefulset-0") to a more concise format (e.g., "gs0")."""
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
        host_name_long = node['id']
        host_name = shorten_node_name(host_name_long)
        hosts[host_name] = net.addHost(host_name)

    # Add links with latency based on the topology
    for link in topology['edges']:
        source_long = link['source']
        source = shorten_node_name(source_long)
        target_long = link['target']
        target = shorten_node_name(target_long)
        latency = link['weight']  # Use 'weight' as latency
        net.addLink(source, target, cls=TCLink, delay=f"{latency}ms")

    net.start()
    return net

def start_socket_server(host, port=5050):
    """
    Starts a socket server to receive messages.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Socket server started on {host}:{port}", flush=True)

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}", flush=True)
                data = conn.recv(1024).decode('utf-8')
                if data:
                    print(f"Received message: {data}", flush=True)
                    logging.info(f"Received message: {data} from {addr}")

def send_socket_message(target_ip, message, port=5050):
    """
    Sends a message to a target node using sockets.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((target_ip, port))
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent message to {target_ip}: '{message}'", flush=True)

def run_gossip_simulation(net, topology):
    """
    Runs a basic gossip simulation on the Mininet network using sockets.
    """
    hosts = {shorten_node_name(node['id']): net.get(shorten_node_name(node['id'])) for node in topology['nodes']}
    print(f"hosts: {hosts}")

    # Start socket servers on all hosts
    for host_name, host in hosts.items():
        host_ip = host.IP()
        threading.Thread(target=start_socket_server, args=(host_ip,)).start()

    # Wait for servers to start
    time.sleep(5)

    # Choose an initial sender
    initial_sender_long = 'gossip-statefulset-0'
    initial_sender = shorten_node_name(initial_sender_long)

    # Send the initial message using sockets
    message = "Hello from Mininet!"
    start_time = time.time_ns()
    send_socket_message(hosts[initial_sender].IP(), message)

    # Wait for the message to propagate
    time.sleep(5)

    # Collect propagation times
    for host_name, host in hosts.items():
        if host_name != initial_sender:
            output = host.cmd('cat /tmp/received_message.txt')
            if output:
                received_time = float(output.splitlines()[-1].split()[-1])
                propagation_time = (received_time - start_time) / 1e6
                logging.info(f"Propagation time to {host_name}: {propagation_time:.2f} ms")

def get_topology(nodes, cluster, model, topology_folder):
    """
    Retrieves the topology file from the specified folder based on the number of nodes and model.
    """
    current_directory = os.getcwd()
    # parent_directory = os.path.dirname(current_directory)
    # topology_dir = os.path.join(parent_directory, topology_folder)
    topology_dir = os.path.join(current_directory, topology_folder)

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
    # Parse command-line arguments
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