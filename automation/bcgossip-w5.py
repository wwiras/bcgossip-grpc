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

def run_command(command, shell=False):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=shell)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)

def apply_kubernetes_config(base_dir, file_path):
    full_path = f"{base_dir}{file_path}"
    command = ['kubectl', 'apply', '-f', full_path]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if 'unchanged' in result.stdout or 'created' in result.stdout:
            print(f"{full_path} applied successfully!", flush=True)
        else:
            print(f"Changes applied to {full_path}:", flush=True)
            print(result.stdout, flush=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while applying {full_path}.", flush=True)
        print(f"Error message: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while applying {full_path}.", flush=True)
        traceback.print_exc()
        sys.exit(1)

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

def access_pod_and_initiate_gossip(pod_name, replicas, unique_id, iteration):
    try:
        session = subprocess.Popen(['kubectl', 'exec', '-it', pod_name, '--', 'sh'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        message = f'{unique_id}-cubaan{replicas}-{iteration}'
        session.stdin.write(f'python initiate.py --message {message}\n')
        session.stdin.flush()
        end_time = time.time() + 300
        while time.time() < end_time:
            reads = [session.stdout.fileno()]
            ready = select.select(reads, [], [], 5)[0]
            if ready:
                output = session.stdout.readline()
                print(output, flush=True)
                if 'Done propagate!' in output:
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

def get_replica_count_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        try:
            replicas = data['spec']['replicas']
            return replicas
        except KeyError:
            return 1  # Default to 1 if no replica count is specified

def wait_for_pods_to_be_ready(namespace='default', expected_pods=0, timeout=300):
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

def main(num_tests, deployment_folder):
    base_dir = "/home/wwiras/bcgossip-grpc/"
    full_directory_path = os.path.join(base_dir, deployment_folder)
    print(f"full_directory_path = {full_directory_path}", flush=True)

    # Modify the path to point to the 'topology' folder
    path_components = full_directory_path.split("/")
    path_components[-2] = 'topology'
    topology_folder = "/".join(path_components)
    topology_folder = "/".join(topology_folder.split("/")[:-1])  # Remove the last component
    print(f"topology_folder={topology_folder}", flush=True)

    # Ensure the path provided is actually a directory
    if not os.path.isdir(full_directory_path):
        print(f"Error: The provided path {full_directory_path} is not a directory.")
        sys.exit(1)

    # List all files in the directory and filter out subdirectories
    deployment_files = [f for f in os.listdir(full_directory_path) if os.path.isfile(os.path.join(full_directory_path, f))]

    if not deployment_files:
        print("No deployment files found in the directory.")
        return False

    for deployment_file in deployment_files:
        deployment_yaml_path = os.path.join(full_directory_path, deployment_file)
        replicas = get_replica_count_from_yaml(deployment_yaml_path)
        print(f"Processing {deployment_file}: Total replicas defined in YAML: {replicas}")

        # Extract the number of nodes from the statefulset filename
        match = re.search(r'(\d+)statefulset', deployment_file)
        print(f"match={match}", flush=True)
        if match:
            num_nodes = int(match.group(1))
            print(f"Detected {num_nodes} nodes from the statefulset filename.")

            # Find the corresponding topology file
            topology_file = None
            for topology_filename in os.listdir(topology_folder):
                if topology_filename.startswith(f'nt_nodes{num_nodes}_'):
                    topology_file = topology_filename
                    break

            if topology_file:
                print(f"Using topology file: {topology_file}")
                full_topology_path = os.path.join(topology_folder, topology_file)

                # Create ConfigMap from the topology file (Using the modified run_command)
                command = [
                    'kubectl', 'create', 'configmap', 'topology-config',
                    '--from-file=' + full_topology_path
                ]
                success, output = run_command(command)
                if success:
                    print("ConfigMap 'topology-config' created successfully!")
                else:
                    print(f"Failed to create ConfigMap. Error: {output}")  # Print the error message
                    return False
            else:
                print(f"No suitable topology file found for {num_nodes} nodes.")
                return False

            # if topology_file:
            #     print(f"Using topology file: {topology_file}")
            #     full_topology_path = os.path.join(topology_folder, topology_file)
            #     print(f"full_topology_path = {full_topology_path}")
            #
            #     # Create ConfigMap from the topology file
            #     command = [
            #         'kubectl', 'create', 'configmap', 'topology-config',
            #         '--from-file=' + full_topology_path
            #     ]
            #     try:
            #         subprocess.run(command, check=True, text=True, capture_output=True)
            #         print("ConfigMap 'topology-config' created successfully!")
            #     except subprocess.CalledProcessError as e:
            #         print(f"Failed to create ConfigMap. Error: {e.stderr}")
            # else:
            #     print(f"No suitable topology file found for {num_nodes} nodes.")
            #     return False

        # Apply configurations (Using run_command)
        root_folder = "/".join(full_directory_path.split("/")[:-2])

        # Check the success of each command and handle errors
        run_command(['kubectl', 'apply', '-f', root_folder + '/svc-bcgossip.yaml'],"svc-bcgossip")
        run_command(['kubectl', 'apply', '-f', root_folder + '/python-role.yaml'])


        # root_folder = "/".join(full_directory_path.split("/")[:-2])
        # print(f"root_folder={root_folder}", flush=True)
        # apply_kubernetes_config(root_folder, '/svc-bcgossip.yaml')
        # apply_kubernetes_config(root_folder, '/python-role.yaml')
        # apply_kubernetes_config(base_dir, deployment_folder + '/' + deployment_file)

        # Ensure pods are ready before proceeding
        # if wait_for_pods_to_be_ready(namespace='default', expected_pods=replicas, timeout=300):
        #     unique_id = str(uuid.uuid4())[:5]  # Generate a unique ID for the entire test
        #     for i in range(1, num_tests + 1):
        #         pod_name = select_random_pod()
        #         print(f"Selected pod for test {i}: {pod_name}", flush=True)
        #         if access_pod_and_initiate_gossip(pod_name, replicas, unique_id, i):
        #             print(f"Test {i} complete for {deployment_file}.", flush=True)
        #         else:
        #             print(f"Test {i} failed for {deployment_file}.", flush=True)
        #     delete_deployment(deployment_yaml_path)
        # else:
        #     print(f"Failed to prepare pods for {deployment_file}.", flush=True)

# def run_command(command):
#     """
#     Runs a command and handles its output and errors.
#
#     Args:
#         command: A list representing the command and its arguments.
#
#     Returns:
#         A tuple (stdout, stderr) if the command succeeds.
#         A tuple (None, stderr) if the command fails.
#     """
#     try:
#         result = subprocess.run(command, check=True, text=True, capture_output=True)
#         # print(result.stdout)  # Print the command's output for visibility
#         return True, result.stdout  # Return both stdout and stderr on success
#     except subprocess.CalledProcessError as e:
#         # print(f"Error executing command: {e.stderr}")
#         return None, e.stderr  # Return None for stdout and the error message on failure

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


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python bcgossip-w5.py <number_of_tests> <deployment_folder>")
        sys.exit(1)
    num_tests = int(sys.argv[1])
    deployment_folder = sys.argv[2]
    result = main(num_tests, deployment_folder)