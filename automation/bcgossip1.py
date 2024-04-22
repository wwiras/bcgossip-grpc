
# Before running this script in the terminal, make sure
# a. Cluster instance is running (based on the specifications of the test)
# b. Enter the terminal through web google cloud terminal
# c. git pull (getting the latest code)
# d. you are ready to run this script


# 1. Set the service
# 2. Set the role python
# For instance name of the deployment and how many round for the test
# The propagation test are
# 4.a Check which deployment are we using and apply it
# Check whether the deployment are ready or not? If problem shows up, halt all
# If ready, proceed to 4.b.
# 4.b Check how many rounds required and test it
# 5. Let say for N round
# 5.a. Get randomly pod name
# 5.b. Enter the pod (from execute terminal command)
# 5.c, Once inside, run python initiate.py --message <message>
# 5.d. Once output done

import subprocess
import sys
import traceback
import random
import time
import select
import yaml

def get_replica_count_from_deployment(base_dir,file_path):
    """
    Read the number of replicas specified in a Kubernetes deployment YAML file.

    Args:
    file_path (str): The path to the Kubernetes deployment YAML file.

    Returns:
    int: The number of replicas specified in the deployment file.
    """
    full_path = f"{base_dir}{file_path}"

    try:
        with open(full_path, 'r') as file:
            deployment = yaml.safe_load(full_path)
            replicas = deployment['spec']['replicas']
            return replicas
    except KeyError as e:
        print(f"Key error while reading the deployment file: {e}")
        return None
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def run_command(command, shell=False):
    """
    Run a shell command and return the output
    """
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=shell)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)

def apply_kubernetes_config_and_wait(base_dir,file_path, expected_count, namespace='default', timeout=600):
    """
    Apply a Kubernetes configuration and wait until all specified pods are running.

    Args:
    file_path (str): The path to the Kubernetes YAML file.
    expected_count (int): The expected number of pods to be running.
    namespace (str): The Kubernetes namespace in which the pods will be running.
    timeout (int): The maximum time to wait for the pods to be running, in seconds.
    """

    full_path = f"{base_dir}{file_path}"

    try:
        # Apply the Kubernetes configuration
        apply_cmd = ['kubectl', 'apply', '-f', file_path]
        subprocess.run(apply_cmd, check=True, text=True, capture_output=True)
        print(f"Applied configuration from {file_path}")

        # Wait for all pods to be in the 'Running' state
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                print("Timeout waiting for all pods to run.")
                return False

            get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers | grep Running | wc -l"
            result = subprocess.run(get_pods_cmd, shell=True, text=True, capture_output=True)
            running_count = int(result.stdout.strip())

            if running_count == expected_count:
                print(f"All {expected_count} pods are running.")
                return True
            else:
                print(f"Currently {running_count}/{expected_count} pods are running. Waiting...")
                time.sleep(10)  # Check every 10 seconds

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while applying configuration or checking pods: {e.stderr}")
        return False

def apply_kubernetes_config(base_dir, file_path):
    """
    Apply a Kubernetes configuration file using kubectl.
    """
    full_path = f"{base_dir}{file_path}"
    command = ['kubectl', 'apply', '-f', full_path]
    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        # Check if the command was successful
        if 'unchanged' in result.stdout or 'created' in result.stdout:
            print(f"{full_path} applied successfully!", flush=True)
        else:
            print(f"Changes applied to {full_path}:", flush=True)
            print(result.stdout, flush=True)

    except subprocess.CalledProcessError as e:
        # Handle errors that result in a non-zero exit code
        print(f"An error occurred while applying {full_path}.", flush=True)
        print(f"Error message: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        # Handle other exceptions
        print(f"An unexpected error occurred while applying {full_path}.", flush=True)
        traceback.print_exc()
        sys.exit(1)

# def delete_deployment(file_path):
#     """
#     Delete a deployment using kubectl without waiting for complete clearance of resources.
#     """
#     command = ['kubectl', 'delete', '-f', file_path]
#     try:
#         # Initiating the deletion of the deployment
#         result = subprocess.run(command, check=True, text=True, capture_output=True)
#         print(f"Deployment deletion initiated and processing for {file_path}.", flush=True)
#         print(f"Deletion output: {result.stdout}", flush=True)
#         if result.stderr:
#             print(f"Deletion error output: {result.stderr}", flush=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to delete deployment from {file_path}. Error: {e.stderr}", flush=True)
#         traceback.print_exc()
#         sys.exit(1)

def delete_deployment(file_path, timeout=300):
    """
    Delete a deployment using kubectl and wait until there are no running pods left in the specified namespace.
    """
    command = ['kubectl', 'delete', '-f', file_path]
    try:
        # Initiating the deletion of the deployment
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Deployment deletion initiated from {file_path}.", flush=True)

        # Monitor the number of running pods
        end_time = time.time() + timeout
        check_command = "kubectl get pod | grep Running | wc -l"
        while time.time() < end_time:
            result = subprocess.run(check_command, shell=True, text=True, capture_output=True)
            if result.stdout.strip() == "0":
                print("All pods are terminated, deletion confirmed.", flush=True)
                return True
            print(f"Waiting for all pods to terminate... Remaining: {result.stdout.strip()}", flush=True)
            time.sleep(0.5)  # wait for 3 seconds before checking again

        print("Timeout waiting for all pods to terminate.", flush=True)
        return False

    except subprocess.CalledProcessError as e:
        print(f"Failed to delete deployment from {file_path}. Error: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)


def select_random_pod():
    """
    Select a random pod from the list of running pods
    """
    command = "kubectl get pods --no-headers | grep Running | awk '{print $1}'"
    pod_list = run_command(command, shell=True).split()
    if not pod_list:
        raise Exception("No running pods found.")
    return random.choice(pod_list)


def access_pod_and_initiate_gossip(pod_name):
    """
    Access the pod's shell, initiate gossip, and handle the response
    """
    try:
        # Starting a shell session in the pod
        session = subprocess.Popen(['kubectl', 'exec', '-it', pod_name, '--', 'sh'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Start the gossip process
        session.stdin.write('python initiate.py --message cubaan10\n')
        session.stdin.flush()

        # Monitor the output until 'Done propagate!' is found or timeout
        end_time = time.time() + 300  # 5 minutes timeout
        while time.time() < end_time:
            reads = [session.stdout.fileno()]
            ready = select.select(reads, [], [], 5)[0]  # Check every 5 seconds
            if ready:
                output = session.stdout.readline()
                print(output, flush=True)
                if 'Done propagate!' in output:
                    print("Gossip propagation complete.", flush=True)
                    break
            if session.poll() is not None:  # Check if process has exited
                print("Session ended before completion.", flush=True)
                break
        else:
            print("Timeout waiting for gossip to complete.", flush=True)
            return False

        # Exiting the shell session
        session.stdin.write('exit\n')
        session.stdin.flush()
        return True

    except Exception as e:
        print(f"Error accessing pod {pod_name}: {e}", flush=True)
        traceback.print_exc()
        return False

def main():
    base_dir = "/home/puluncode/bcgossip-grpc/"
    # Apply the role for the Python script
    apply_kubernetes_config(base_dir, 'k8sv2/python-role.yaml')

    # Deploy the main application
    apply_kubernetes_config(base_dir, 'k8sv2/svc-bcgossip.yaml')

    # Deploy the 10-node gossip protocol environment
    # apply_kubernetes_config(base_dir, 'k8sv2/deploy-10nodes.yaml')

    # Read the number of replicas specified in a Kubernetes deployment YAML file.
    replica_count = get_replica_count_from_deployment(base_dir, 'k8sv2/deploy-10nodes.yaml')
    print(f"Number of replicas specified in the deployment: {replica_count}")

    # Deploy the 10-node gossip protocol environment
    apply_kubernetes_config_and_wait(base_dir, 'k8sv2/deploy-10nodes.yaml')


    # Select and access pod to initiate gossip
    pod_name = select_random_pod()
    print(f"Selected pod: {pod_name}", flush=True)
    if access_pod_and_initiate_gossip(pod_name):
        # Only delete the deployment if gossip was successfully initiated
        delete_deployment(f"{base_dir}k8sv2/deploy-10nodes.yaml")
    else:
        print("Gossip initiation failed.", flush=True)


if __name__ == '__main__':
    main()
