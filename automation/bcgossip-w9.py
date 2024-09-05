import os
import subprocess
import sys
import traceback
import random
import time
import select
import yaml
import uuid
import re

def delete_deployment(file_path, namespace='default', timeout=300):
    command = ['kubectl', 'delete', '-f', file_path, '-n', namespace]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Deployment deletion initiated for {file_path}.", flush=True)

        start_time = time.time()
        get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers"

        while time.time() - start_time < timeout:
            result = subprocess.run(get_pods_cmd, shell=True, text=True, capture_output=True, check=True)
            if len(result.stdout.strip()) == 0:
                print("No pods found in the namespace, deletion confirmed.", flush=True)
                return True

            print("Waiting for all pods to terminate...", flush=True)
            time.sleep(10)

        print("Timeout waiting for the resources to clear from the namespace.", flush=True)
        return False

    except subprocess.CalledProcessError as e:
        print(f"Failed to delete deployment from {file_path}. Error: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)

def select_random_pod():
    command = "kubectl get pods --no-headers | grep Running | awk '{print $1}'"
    pod_list = run_command(command, shell=True).split()
    if not pod_list:
        raise Exception("No running pods found.")
    return random.choice(pod_list)

def access_pod_and_initiate_gossip(pod_name, replicas, speed, unique_id, iteration):
    try:
        session = subprocess.Popen(['kubectl', 'exec', '-it', pod_name, '--', 'sh'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        message = f'{unique_id}-{replicas}Nodes{speed}-{iteration}'
        session.stdin.write(f'python3 start.py --message {message}\n')
        session.stdin.flush()
        end_time = time.time() + 300
        while time.time() < end_time:
            reads = [session.stdout.fileno()]
            ready = select.select(reads, [], [], 5)[0]
            if ready:
                output = session.stdout.readline()
                print(output, flush=True)
                if 'Received acknowledgment:' in output:
                    print("Gossip propagation complete.", flush=True)
                    break
            if session.poll() is not None:
                print("Session ended before completion.", flush=True)
                break
        else:
            print("Timeout waiting for gossip to complete.", flush=True)
            return False
        session.stdin.write('exit\n')
        session.stdin.flush()
        return True
    except Exception as e:
        print(f"Error accessing pod {pod_name}: {e}", flush=True)
        traceback.print_exc()
        return False

def wait_for_pods_to_be_ready(namespace='default', expected_pods=0, timeout=300):
    """
    Waits for all pods in the specified StatefulSet to be ready.
    """
    start_time = time.time()
    get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers | grep Running | wc -l"

    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(get_pods_cmd, shell=True, text=True, capture_output=True, check=True)
            running_pods = int(result.stdout.strip())

            if running_pods >= expected_pods:
                print(f"All {expected_pods} pods are running in namespace {namespace}.", flush=True)
                return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to get pod status for namespace {namespace}. Error: {e.stderr}", flush=True)
        time.sleep(10)  # Check every 10 seconds

    print(f"Timeout waiting for all {expected_pods} pods to be running in namespace {namespace}.", flush=True)
    return False


def apply_tc_rules(pod_name, pod_ips, topology, interface="eth0"):
    """
    Applies tc rules to limit bandwidth between neighboring pods based on topology data.

    Args:
        pod_name: The name of the pod.
        pod_ips: A list of IP addresses of all pods in the StatefulSet.
        topology: The network topology data (assuming it's a dictionary loaded from JSON).
        interface: The network interface to apply tc rules to (default: "eth0").
    """

    neighbor_pods = [ip for ip in pod_ips if ip != get_pod_ip(pod_name)]

    for neighbor_ip in neighbor_pods:
        # Get bandwidth limit from topology (adjust based on your topology structure)
        bandwidth_mbps = next(
            (link["bandwidth"] for link in topology["links"]
             if (link["source"] == pod_name and link["target"] == neighbor_pod_name) or
                (link["target"] == pod_name and link["source"] == neighbor_pod_name)),
            None  # Default if no matching link is found
        )

        if bandwidth_mbps is None:
            print(f"Warning: No bandwidth limit found in topology for connection {pod_name} to {neighbor_pod_name}. Skipping tc rule application.")
            continue

        print(f"Applying tc rules on {pod_name} for neighbor {neighbor_ip} with speed {bandwidth_mbps}Mbps...")

        # Construct tc commands as a list
        tc_commands = [
            "tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", "htb", "default", "12",
            "tc", "class", "add", "dev", interface, "parent", "1:", "classid", "1:1", "htb",
                "rate", f"{bandwidth_mbps}mbit", "ceil", f"{bandwidth_mbps}mbit",
            "tc", "filter", "add", "dev", interface, "parent", "1:", "protocol", "ip", "prio", "1", "u32",
                "match", "ip", "dst", neighbor_ip, "flowid", "1:1"
        ]

        try:
            result = subprocess.run(tc_commands, check=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully applied tc rules on {pod_name} for neighbor {neighbor_ip}")
            else:
                print(f"Error applying tc rules on {pod_name}: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Error applying tc rules on {pod_name}: {e.stderr}")

def run_command(command, full_path=None):
    """
    Runs a command and handles its output and errors.

    Args:
        command: A list representing the command and its arguments.
        full_path: (Optional) The full path to a file being processed
                   (used for informative messages in case of 'apply' commands).

    Returns:
        A tuple (stdout, stderr) if the command succeeds.
        A tuple (None, stderr) if the command fails.
    """
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        # If full_path is provided (likely for 'apply' commands), provide more informative output
        if full_path:
            if 'unchanged' in result.stdout or 'created' in result.stdout:
                print(f"{full_path} applied successfully!", flush=True)
            elif 'deleted' in result.stdout:
                print(f"{full_path} deleted successfully!", flush=True)
            else:
                print(f"Changes applied to {full_path}:", flush=True)
                print(result.stdout, flush=True)

        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        if full_path:
            print(f"An error occurred while applying {full_path}.", flush=True)
        else:
            print(f"An error occurred while executing the command.", flush=True)
        print(f"Error message: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        if full_path:
            print(f"An unexpected error occurred while applying {full_path}.", flush=True)
        else:
            print(f"An unexpected error occurred while executing the command.", flush=True)
        traceback.print_exc()
        sys.exit(1)

def get_topology(self, total_replicas, topology_folder):
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

def get_pod_names_and_ips(namespace,num_nodes):
    """
    Retrieves the names and IP addresses of pods in the specified namespace using kubectl.

    Args:
        namespace: The namespace where the pods are located (default: "default").

    Returns:
        A dictionary where keys are pod names and values are their corresponding IP addresses.
        An empty dictionary if no pods are found or an error occurs.
    """
    command = [
        "kubectl",
        "get",
        "pods",
        "-n",
        namespace,
        "-o",
        "jsonpath='{range .items[*]}{@.metadata.name} {.status.podIP}{\"\\n\"}{end}'",
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        output = result.stdout.strip()
        # print(output)

        pod_info = {}
        for line in output.splitlines():
            # print(line)
            # print(len(pod_info))
            if len(pod_info)<num_nodes:
                print(line.split())
                pod_name, pod_ip = line.split()
                pod_info[pod_name] = pod_ip

        return pod_info

    except subprocess.CalledProcessError as e:
        print(f"Error getting pod names and IPs: {e.stderr}", flush=True)
        return {}

def main(num_tests, deployment_folder):
    # base directory of our main gossip folder path
    base_dir = "/home/wwiras/bcgossip-grpc/"
    print(f"base_dir = {base_dir}", flush=True)

    # deployment folder path
    deployment_path = os.path.join(base_dir, deployment_folder)
    print(f"deployment_path = {deployment_path}", flush=True)

    # root folder (k8swx folder) path
    root_folder = "/".join(deployment_path.split("/")[:-2])
    print(f"root_folder = {root_folder}", flush=True)

    # Ensure the path provided is actually a directory
    if not os.path.isdir(deployment_path):
        print(f"Error: The provided path {deployment_path} is not a directory.",flush=True)
        sys.exit(1)

    # List all files in the directory and filter out subdirectories
    deployment_files = [f for f in os.listdir(deployment_path) if os.path.isfile(os.path.join(deployment_path, f))]

    # Check if deployment files found or not
    if not deployment_files:
        print("No deployment files found in the directory.")
        return False

    # Apply service and python role
    run_command(['kubectl', 'apply', '-f', root_folder + '/svc-bcgossip.yaml'], "svc-bcgossip")
    run_command(['kubectl', 'apply', '-f', root_folder + '/python-role.yaml'], "python-role")

    # Getting total replicas from deployment file
    for deployment_file in deployment_files:

        # Extract the number of nodes from the statefulset filename
        match = re.search(r'(\d+)statefulset', deployment_file)
        if match:
            num_nodes = int(match.group(1))
            print(f"Detected {num_nodes} nodes from the statefulset: {deployment_file}.", flush=True)
            if num_nodes!=10:
                continue
        else:
            print(f"Error: Could not extract num_nodes from {deployment_file} filename.", flush=True)
            return False

        # Extract the speed (like 1M, 3M, 5M, 10M or RM-random bwidth) from the statefulset filename
        match = re.search(r'(\d+M|RM)', deployment_file)
        if match:
            speed = match.group(1)
            print(f"Extracted speed: {speed} from {deployment_file}", flush=True)
        else:
            print(f"Speed pattern not found in the filename : {deployment_file}", flush=True)
            return False

        # Get deployment file
        deployment_yaml_file = os.path.join(deployment_path, deployment_file)
        print(f"deployment_yaml_file={deployment_yaml_file}", flush=True)

        # Apply statefulset
        run_command(['kubectl', 'apply', '-f', deployment_yaml_file], deployment_file)

        # Ensure pods are ready before proceeding
        if wait_for_pods_to_be_ready(namespace='default', expected_pods=num_nodes, timeout=300):

            # Get statefulset pod names and ips
            statefulsets = get_pod_names_and_ips("default",num_nodes)

            # --- Apply tc rules directly ---
            for statefulset_podname, statefulset_podip  in statefulsets:
                run_command(['kubectl', 'exec', '-it', statefulset_podname + '-- python3 tc_setup.py ' + str(num_nodes)])

            # --- Original gossip initiation logic ---
            unique_id = str(uuid.uuid4())[:5]  # Generate a unique ID for the entire test
            for i in range(1, num_tests + 1):
                pod_name = "gossip-statefulset-0"
                print(f"Selected pod for test {i}: {pod_name}", flush=True)
                if access_pod_and_initiate_gossip(pod_name, num_nodes, speed, unique_id, i):
                    print(f"Test {i} complete for {deployment_file}.", flush=True)
                else:
                    print(f"Test {i} failed for {deployment_file}.", flush=True)
            delete_deployment(deployment_yaml_file)
        else:
            print(f"Failed to prepare pods for {deployment_file}.", flush=True)

    # Delete service and python role
    run_command(['kubectl', 'delete', '-f', root_folder + '/svc-bcgossip.yaml'], "svc-bcgossip")
    run_command(['kubectl', 'delete', '-f', root_folder + '/python-role.yaml'], "python-role")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python bcgossip-w9.py <number_of_tests> <deployment_folder>")
        sys.exit(1)
    num_tests = int(sys.argv[1])
    deployment_folder = sys.argv[2]
    result = main(num_tests, deployment_folder)