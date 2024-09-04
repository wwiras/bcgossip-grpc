from kubernetes import client, config
import os
import socket
import json

def get_topology(total_replicas, topology_folder, statefulset_name="gossip-statefulset", namespace="default"):
    """
    Retrieves the number of replicas for the specified StatefulSet using kubectl
    and finds the corresponding topology file in the 'topology' subfolder
    within the current working directory.
    """

    # Get the current working directory
    current_directory = os.getcwd()

    # Construct the full path to the topology folder
    topology_folder = os.path.join(current_directory, topology_folder)

    # Find the corresponding topology file
    topology_file = None
    for topology_filename in os.listdir(topology_folder):
        if topology_filename.startswith(f'nt_nodes{total_replicas}_'):
            topology_file = topology_filename
            break

    if topology_file:
        with open(os.path.join(topology_folder, topology_file), 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"No topology file found for {total_replicas} nodes.")

def get_pod_ip(pod_name, namespace="default"):
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    return pod.status.pod_ip

def _find_neighbors(node_id, topology):
        """
        Identifies the neighbors of the given node based on the topology,
        including the bandwidth of the connection.
        """
        neighbors = []
        for link in topology['links']:
            if link['source'] == node_id:
                neighbors.append((link['target'], link['bandwidth']))
            elif link['target'] == node_id:
                neighbors.append((link['source'], link['bandwidth']))
        return neighbors