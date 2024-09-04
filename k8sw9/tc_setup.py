import json
import os
import subprocess
import sys

from kubernetes import client, config


def get_topology(total_replicas, topology_folder):
    """
    Retrieves the topology for the specified number of replicas from the given topology folder.
    """
    current_directory = os.getcwd()
    topology_folder = os.path.join(current_directory, topology_folder)

    topology_file = None
    for topology_filename in os.listdir(topology_folder):
        if topology_filename.startswith(f'nt_nodes{total_replicas}_'):
            topology_file = topology_filename
            break

    if topology_file:
        with open(os.path.join(topology_folder, topology_file), 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"No topology file found for {total_replicas} nodes in {topology_folder}.")


def get_pod_ip(pod_name, namespace="default"):
    """
    Retrieves the IP address of the specified pod using kubectl.
    """
    result = subprocess.run(
        [
            "kubectl",
            "get",
            "pods",
            "-n",
            namespace,
            pod_name,
            "-o",
            "jsonpath='{.status.podIP}'",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip("'")
    else:
        raise RuntimeError(f"Failed to get IP for pod {pod_name}: {result.stderr}")


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


def apply_tc_rules(interface="eth0"):
    """
    Applies tc rules based on the network topology and bandwidth limits.
    """
    pod_name = os.environ.get("HOSTNAME")

    if len(sys.argv) < 2:
        raise ValueError("Total number of replicas not provided as an argument")
    total_replicas = int(sys.argv[1])

    topology_folder = 'topology/' + os.environ['BANDWIDTH_LIMIT']
    topology = get_topology(total_replicas, topology_folder)

    neighbors = _find_neighbors(pod_name, topology)

    for neighbor_pod_name, bandwidth_mbps in neighbors:
        neighbor_ip = get_pod_ip(neighbor_pod_name)

        # Apply tc rules (adjust commands if needed)
        subprocess.run(["tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", "htb", "default", "12"])
        subprocess.run(
            [
                "tc",
                "class",
                "add",
                "dev",
                interface,
                "parent",
                "1:",
                "classid",
                "1:1",
                "htb",
                "rate",
                f"{bandwidth_mbps}mbit",
                "ceil",
                f"{bandwidth_mbps}mbit",
            ]
        )
        subprocess.run(
            [
                "tc",
                "filter",
                "add",
                "dev",
                interface,
                "parent",
                "1:",
                "protocol",
                "ip",
                "prio",
                "1",
                "u32",
                "match",
                "ip",
                "dst",
                neighbor_ip,
                "flowid",
                "1:1",
            ]
        )

        print(f"Applied tc rules for {pod_name} to {neighbor_pod_name} with bandwidth {bandwidth_mbps} Mbps")


if __name__ == "__main__":
    apply_tc_rules()