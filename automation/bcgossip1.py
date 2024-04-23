import subprocess
import sys
import traceback
import random
import time
import select


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


def delete_deployment(file_path, namespace='default', timeout=300):
    """
    Delete a deployment using kubectl and wait until no resources are found in the specified namespace.
    """
    command = ['kubectl', 'delete', '-f', file_path]
    try:
        # Initiating the deletion of the deployment
        subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Deployment deletion initiated from {file_path}.", flush=True)

        # Monitor for "No resources found" message
        end_time = time.time() + timeout
        while time.time() < end_time:
            check_command = ['kubectl', 'get', 'pods', '-n', namespace]
            result = subprocess.run(check_command, text=True, capture_output=True)
            if "No resources found" in result.stdout:
                print("No resources found in the namespace, deletion confirmed.", flush=True)
                return True
            time.sleep(0.5)  # wait for 5 seconds before checking again

        print("Timeout waiting for the resources to clear from the namespace.", flush=True)
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
    apply_kubernetes_config(base_dir, 'k8sv2/deploy-10nodes.yaml')

    # Select and access pod to initiate gossip
    pod_name = select_random_pod()
    print(f"Selected pod: {pod_name}", flush=True)
    if access_pod_and_initiate_gossip(pod_name):
        # Only delete the deployment if gossip was successfully initiated
        delete_deployment(f"{base_dir}k8sv2/deploy-10nodes.yaml")


if __name__ == '__main__':
    main()
