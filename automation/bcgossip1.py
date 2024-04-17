
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


def delete_deployment(file_path):
    """
    Delete a deployment using kubectl.
    """
    command = ['kubectl', 'delete', '-f', file_path]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"Deployment successfully deleted from {file_path}.", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete deployment from {file_path}. Error: {e.stderr}", flush=True)
        traceback.print_exc()
        sys.exit(1)


def get_running_pods_count():
    """
    Get the count of pods that are in the Running state
    """
    command = "kubectl get pod | grep Running | wc -l"
    count = run_command(command, shell=True)
    return int(count)


def select_random_pod():
    """
    Select a random pod from the list of running pods
    """
    command = "kubectl get pod --no-headers | grep Running | awk '{print $1}'"
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

        # Sending the command to initiate gossip
        out, err = session.communicate('python initiate.py --message cubaan10\n')
        if 'Done propagate!' in out:
            print("Gossip propagation complete.", flush=True)
            return True
        else:
            print("Gossip did not complete as expected.", flush=True)
            print(err, flush=True)
            return False

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

    # Ensure all pods are running
    if get_running_pods_count() == 10:
        pod_name = select_random_pod()
        print(f"Selected pod: {pod_name}", flush=True)
        if access_pod_and_initiate_gossip(pod_name):
            # Only delete the deployment if gossip was successfully initiated
            delete_deployment(f"{base_dir}k8sv2/deploy-10nodes.yaml")
    else:
        print("The number of running pods is not equal to 10.", flush=True)


if __name__ == '__main__':
    main()
