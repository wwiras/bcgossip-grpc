import argparse
import json
import subprocess
import sys
import traceback
import time
import uuid
import select
import random
from datetime import datetime, timedelta, timezone


class Test:
    def __init__(self, num_tests, num_nodes):
        # Getting test details
        self.num_tests = num_tests
        self.num_nodes = num_nodes
        print(f"self.num_test = {self.num_tests}", flush=True)
        print(f'self.num_nodes = {self.num_nodes}', flush=True)

    def run_command(self, command, full_path=None, suppress_output=False):
        """
        Runs a command and handles its output and errors.

        Args:
            command: A list representing the command and its arguments.
            full_path: (Optional) The full path to a file being processed
                       (used for informative messages in case of 'apply' commands).
            suppress_output: (Optional) If True, suppresses printing the stdout of the command.

        Returns:
            A tuple (stdout, stderr) if the command succeeds.
            A tuple (None, stderr) if the command fails.
        """
        try:
            if isinstance(command, str):
                result = subprocess.run(command, check=True, text=True, capture_output=True, shell=True)
            else:
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

            # Print stdout only if suppress_output is False
            if not suppress_output:
                print(f"result.stdout: {result.stdout}", flush=True)

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

    def wait_for_pods_to_be_ready(self, namespace='default', expected_pods=0, timeout=1000):
        """
        Waits for all pods in the specified namespace to be ready.
        """
        print(f"Checking for pods in namespace {namespace}...", flush=True)
        start_time = time.time()
        get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers | grep Running | wc -l"

        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(get_pods_cmd, shell=True,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                running_pods = int(result.stdout.strip())
                if running_pods >= expected_pods:
                    print(f"All {expected_pods} pods are up and running in namespace {namespace}.", flush=True)
                    return True
                else:
                    print(f" {running_pods} pods are up for now in namespace {namespace}. Waiting...", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"Error checking for pods: {e.stderr}", flush=True)
                return False
            time.sleep(1)
        print(f"Timeout waiting for pods to terminate in namespace {namespace}.", flush=True)
        return False

    def wait_for_pods_to_be_down(self, namespace='default', timeout=1000):
        """
        Waits for all pods in the specified namespace to be down.
        """
        print(f"Checking for pods in namespace {namespace}...", flush=True)
        start_time = time.time()
        get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers | grep Terminating | wc -l"

        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(get_pods_cmd, shell=True,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if "No resources found" in result.stderr:
                    print(f"No pods found in namespace {namespace}.", flush=True)
                    return True
                else:
                    print(f"Pods still exist in namespace {namespace}. Waiting...", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"Error checking for pods: {e.stderr}", flush=True)
                return False
            time.sleep(1)
        print(f"Timeout waiting for pods to terminate in namespace {namespace}.", flush=True)
        return False

    def select_random_pod(self):
        """
        Select a random pod from the list of running pods.
        """
        command = "kubectl get pods --no-headers | grep Running | awk '{print $1}'"
        stdout, stderr = self.run_command(command, suppress_output=True)  # Suppress stdout for this command
        pod_list = stdout.split()  # Split the stdout into a list of pod names
        if not pod_list:
            raise Exception("No running pods found.")
        return random.choice(pod_list)  # Return a random pod name


    def _get_malaysian_time(self):
        """Helper function to get the current time in Malaysian timezone (UTC+8)."""
        utc_time = datetime.now(timezone.utc)  # Get current UTC time
        malaysia_offset = timedelta(hours=8)  # Malaysia is UTC+8
        malaysia_time = utc_time + malaysia_offset
        return malaysia_time

    def access_pod_and_initiate_gossip(self, pod_name, replicas, unique_id, iteration):
        """
        Access the pod's shell, initiate gossip, and handle the response.
        """
        try:
            # Log the start of gossip propagation in Malaysian time
            start_time = self._get_malaysian_time().strftime('%Y-%m-%d %H:%M:%S')
            message = f'{unique_id}-cubaan{replicas}-{iteration}'
            start_log = {
                'event': 'gossip_start',
                'pod_name': pod_name,
                'message': message,
                'start_time': start_time,
                'details': f"Gossip propagation started for message: {message}"
            }
            print(json.dumps(start_log), flush=True)  # Log the start event

            # Start the session with the pod
            session = subprocess.Popen(['kubectl', 'exec', '-it', pod_name, '--request-timeout=600',
                                        '--', 'sh'], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Send the gossip message to the pod
            session.stdin.write(f'python3 start.py --message {message}\n')
            session.stdin.flush()

            # Wait for the gossip to complete
            # end_time = time.time() + 300
            # end_time = time.time() + 1200
            end_time = time.time() + 1600
            while time.time() < end_time:
                reads = [session.stdout.fileno()]
                ready = select.select(reads, [], [], 5)[0]
                if ready:
                    output = session.stdout.readline()
                    print(output, flush=True)
                    if 'Received acknowledgment:' in output:
                        # Log the end of gossip propagation in Malaysian time
                        end_time_log = self._get_malaysian_time().strftime('%Y-%m-%d %H:%M:%S')
                        end_log = {
                            'event': 'gossip_end',
                            'pod_name': pod_name,
                            'message': message,
                            'end_time': end_time_log,
                            'details': f"Gossip propagation completed for message: {message}"
                        }
                        print(json.dumps(end_log), flush=True)  # Log the end event
                        break
                if session.poll() is not None:
                    print("Session ended before completion.", flush=True)
                    break
            else:
                print("Timeout waiting for gossip to complete.", flush=True)
                return False

            # Close the session
            session.stdin.write('exit\n')
            session.stdin.flush()
            return True

        except Exception as e:
            # Log any errors that occur during gossip propagation
            error_log = {
                'event': 'gossip_error',
                'pod_name': pod_name,
                'message': message,
                'error': str(e),
                'details': f"Error accessing pod {pod_name}: {e}"
            }
            print(json.dumps(error_log), flush=True)  # Log the error event
            traceback.print_exc()
            return False

if __name__ == '__main__':
    # Getting the input or setting
    parser = argparse.ArgumentParser(description="Usage: python automate.py --num_test <number_of_tests>")
    parser.add_argument('--num_tests', required=True, type=int, help="Total number of tests to do")
    parser.add_argument('--num_nodes', required=True, type=int, help="Total number of nodes")
    args = parser.parse_args()

    test = Test(args.num_tests, args.num_nodes)  # Pass the new arguments to Test

    # Helm name is fixed
    helmname = 'cnsim'

    if test.wait_for_pods_to_be_down(namespace='default', timeout=1000):
        # Apply helm
        result = test.run_command(['helm', 'install', helmname, 'chartsim/', '--values',
                                   'chartsim/values.yaml', '--debug',
                                   '--set', 'totalNodes=' + str(test.num_nodes)])

        print(f"Helm {helmname} started...", flush=True)

        if test.wait_for_pods_to_be_ready(namespace='default', expected_pods=test.num_nodes, timeout=1000):
            # Create unique uuid for this test
            unique_id = str(uuid.uuid4())[:4]  # Generate a UUID and take the first 4 characters

            # Test iteration starts here
            # iteration=0 for convergence
            for nt in range(0, test.num_tests + 1):
                pod_name = test.select_random_pod()
                print(f"Selected pod: {pod_name}", flush=True)
                if test.access_pod_and_initiate_gossip(pod_name, test.num_nodes, unique_id, nt):
                    print(f"Test {nt} complete.", flush=True)
                else:
                    print(f"Test {nt} failed.", flush=True)
        else:
            print(f"Failed to prepare pods for {helmname}.", flush=True)

        # Remove helm
        result = test.run_command(['helm', 'uninstall', helmname])
        print(f"Helm {helmname} will be uninstalled...", flush=True)
        if test.wait_for_pods_to_be_down(namespace='default', timeout=1000):
            print(f"Helm {helmname} uninstallation is complete...", flush=True)
    else:
        print(f"No file was found for args={args}")