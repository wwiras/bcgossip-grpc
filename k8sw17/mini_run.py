from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
import time
import json
import logging
import os
import argparse

# Configure logging
logging.basicConfig(filename='gossip_simulation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_mininet_network(topology):
    """
    Creates a Mininet network based on the provided topology.
    """
    net = Mininet(controller=Controller)
    net.addController('c0')

    # Add hosts (nodes) based on the topology
    hosts = {}
    for node in topology['nodes']:
        host_name = node['id']  # Assuming 'id' is the host name in your JSON
        hosts[host_name] = net.addHost(host_name)

    # Add links with bandwidth and latency based on the topology
    for link in topology['edges']:
        source = hosts[link['source']]
        target = hosts[link['target']]
        # bandwidth = link.get('bandwidth', 10)  # Default bandwidth if not specified
        # latency = link.get('latency', '10ms')   # Default latency if not specified
        # net.addLink(source, target, cls=TCLink, bw=bandwidth, delay=latency)
        latency = link['weight'] # in this case the weight is latency
        net.addLink(source, target, cls=TCLink,delay=latency)

    net.start()
    return net

def run_gossip_simulation(net, topology):
    """
    Runs a basic gossip simulation on the Mininet network.
    """
    hosts = {node['id']: net.get(node['id']) for node in topology['nodes']}  # Get host objects

    # Choose an initial sender (you can modify this)
    initial_sender = 'gossip-statefulset-0'  # Replace with the actual name of your initial sender

    # Send the initial message
    message = "Hello from Mininet!"
    start_time = time.time_ns()
    hosts[initial_sender].cmd(f'python3 -c "import socket; sock = socket.socket(); sock.connect((\'{hosts[initial_sender].IP()}\', 5050)); sock.send(b\'{message}\'); sock.close()"')

    # Wait for the message to propagate (you might need to adjust the timeout)
    time.sleep(5)

    # Collect propagation times (implementation depends on your gossip logic)
    # For this example, we'll just print the time when each host received the message
    for host_name, host in hosts.items():
        if host_name!= initial_sender:
            output = host.cmd('cat /tmp/received_message.txt')  # Assuming you're writing the received message to a file
            if output:
                received_time = float(output.splitlines()[-1].split()[-1])  # Extract the timestamp from the output
                propagation_time = (received_time - start_time) / 1e6  # in milliseconds
                logging.info(f"Propagation time to {host_name}: {propagation_time:.2f} ms")  # Log the propagation time

    def get_topology(self,topology_folder):
        """
        Retrieves the topology file from the specified folder based on the number of nodes and model.
        """
        current_directory = os.getcwd()
        topology_dir = os.path.join(current_directory, topology_folder)

        # Construct the search string based on the cluster and model
        search_str = f'nodes{self.total_nodes}_' if self.cluster == '0' else f'kmeans_nodes{self.total_nodes}_'

        # Find the corresponding topology file
        topology_file = None
        for topology_filename in os.listdir(topology_dir):
            if topology_filename.startswith(search_str) and self.model in topology_filename:
                topology_file = topology_filename
                break

        if topology_file:
            with open(os.path.join(topology_dir, topology_file), 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"No topology file found for {self.total_nodes} nodes and model {self.model}.")

def get_topology(nodes,cluster,model,topology_folder):
    """
    Retrieves the topology file from the specified folder based on the number of nodes and model.
    """
    current_directory = os.getcwd()
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

    # get all args: cluster type, model, and totalnodes
    parser = argparse.ArgumentParser(description="Run a gossip on mininet.")
    parser.add_argument('--cluster', required=True, choices=['0', '1'],help="Cluster type: 0 for non-clustered, 1 for k-means clustered")
    parser.add_argument('--model', required=True, choices=['BA', 'ER'], help="Topology model: BA or ER")
    parser.add_argument('--nodes', required=True, type=int, help="Total number of nodes in the topology")
    args = parser.parse_args()

    # Determine the topology folder based on cluster type
    topology_folder = "topology" if args.cluster == '0' else "topology_kmeans"

    # get topology file based on input
    topology = get_topology(args.nodes,args.cluster,args.model,topology_folder)
    print(f"topology={topology}",flush=True)

    net = create_mininet_network(topology)  # Create the Mininet network
    # run_gossip_simulation(net, topology)   # Run the gossip simulation
    net.stop()                            # Stop the network