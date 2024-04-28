import os
import subprocess
import sys
import traceback
import random
import time
import select
import yaml
import uuid

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

import os
import sys

def main(num_tests, deployment_folder):
    base_dir = "/home/puluncode/bcgossip-grpc/"
    full_directory_path = os.path.join(base_dir, deployment_folder)

    # Ensure the path provided is actually a directory
    if not os.path.isdir(full_directory_path):
        print(f"Error: The provided path {full_directory_path} is not a directory.")
        sys.exit(1)

    # List all files in the directory and filter out subdirectories
    deployment_files = [f for f in os.listdir(full_directory_path) if os.path.isfile(os.path.join(full_directory_path, f))]

    for deployment_file in deployment_files:
        deployment_yaml_path = os.path.join(full_directory_path, deployment_file)

        # Continue with existing logic
        replicas = get_replica_count_from_yaml(deployment_yaml_path)
        print(f"Total replicas defined in YAML: {replicas}")

        # Apply configurations, manage tests, etc.

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python bcgossip-sim.py <number_of_tests> <deployment_folder>")
        sys.exit(1)
    num_tests = int(sys.argv[1])
    deployment_folder = sys.argv[2]
    main(num_tests, deployment_folder)
