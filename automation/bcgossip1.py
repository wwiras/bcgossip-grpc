import subprocess
import sys
import traceback
import random
import time
import select
import yaml

def run_command(command, shell=False):
    """
    Run a shell command and return the output.
    """
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True, shell=shell)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)

def apply_kubernetes_config(base_dir, file_path):
    """
    Apply a Kubernetes configuration file using kubectl.
    """
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
    """
    Delete a deployment using kubectl and monitor until "No resources found" message is detected in the namespace.
    """
    command = ['kubectl', 'delete', '-f', file_path, '-n', namespace]
    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Deployment deletion initiated for {file_path}.", flush=True)

        start_time = time.time()
        # get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers"
        get_pods_cmd = f"kubectl get pods"

        while time.time() - start_time < timeout:
            result = subprocess.run(get_pods_cmd, shell=True, text=True, capture_output=True, check=True)
            print(result.stdout, flush=True)
            if "No resources found" in result.stdout:
                print("No resources found in the namespace, deletion confirmed.", flush=True)
                return True

            print("Waiting for all pods to terminate...", flush=True)
            time.sleep(0.5)  # Update status every 2 seconds

        print("Timeout waiting for the resources to clear from the namespace.", flush=True)
        return False

    except subprocess.CalledProcessError as e:
        print(f"Failed to delete deployment from {file_path}. Error: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)


def select_random_pod():
    """
    Select a random pod from the list of running pods.
    """
    command = "kubectl get pods --no-headers | grep Running | awk '{print $1}'"
    pod_list = run_command(command, shell=True).split()
    if not pod_list:
        raise Exception("No running pods found.")
    return random.choice(pod_list)

def access_pod_and_initiate_gossip(pod_name):
    """
    Access the pod's shell, initiate gossip, and handle the response.
    """
    try:
        session = subprocess.Popen(['kubectl', 'exec', '-it', pod_name, '--', 'sh'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        session.stdin.write('python initiate.py --message cubaan10\n')
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
    """
    Read the Kubernetes deployment YAML file and return the replica count.
    """
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        try:
            replicas = data['spec']['replicas']
            return replicas
        except KeyError:
            return 1  # Default to 1 if no replica count is specified

def wait_for_pods_to_be_ready(namespace='default', expected_pods=0, timeout=300):
    """
    Wait for a specific number of pods to reach the 'Running' state in a given namespace.
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
        time.sleep(1)  # Check every 10 seconds

    print(f"Timeout waiting for all {expected_pods} pods to be running in namespace {namespace}.", flush=True)
    return False


def main():
    base_dir = "/home/puluncode/bcgossip-grpc/"
    deployment_yaml_path = base_dir + 'k8sv2/deploy-10nodes.yaml'

    # Get the replica count from the YAML file
    replicas = get_replica_count_from_yaml(deployment_yaml_path)
    print(f"Total replicas defined in YAML: {replicas}")

    # Apply configurations
    apply_kubernetes_config(base_dir, 'k8sv2/python-role.yaml')
    apply_kubernetes_config(base_dir, 'k8sv2/svc-bcgossip.yaml')
    apply_kubernetes_config(base_dir, 'k8sv2/deploy-10nodes.yaml')

    # Ensure pods are ready before proceeding
    if wait_for_pods_to_be_ready(namespace='default', expected_pods=replicas, timeout=300):
        pod_name = select_random_pod()
        print(f"Selected pod: {pod_name}", flush=True)
        if access_pod_and_initiate_gossip(pod_name):
            delete_deployment(deployment_yaml_path)

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
