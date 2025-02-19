from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
import time
import json
import logging

# Configure logging
logging.basicConfig(filename='gossip_simulation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the topology from the JSON file
with open('network_topology.json', 'r') as f:
    topology = json.load(f)

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
    for link in topology['links']:
        source = hosts[link['source']]
        target = hosts[link['target']]
        # bandwidth = link.get('bandwidth', 10)  # Default bandwidth if not specified
        latency = link.get('latency', '10ms')   # Default latency if not specified
        # net.addLink(source, target, cls=TCLink, bw=bandwidth, delay=latency)
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

if __name__ == '__main__':
    net = create_mininet_network(topology)  # Create the Mininet network
    # run_gossip_simulation(net, topology)   # Run the gossip simulation
    net.stop()                            # Stop the network