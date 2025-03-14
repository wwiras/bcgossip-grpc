import os
import argparse
import re
import subprocess
import sys
import traceback
import time
import uuid
import select

class Test:
    def __init__(self,num_test,cluster):

        # Getting topology folder
        # 0 - for non cluster, 1 - for cluster topology
        if cluster == '0':
            self.topology_folder_only = 'topology'
            self.cluster = 0
        else:
            self.topology_folder_only = 'topology_kmeans'
            self.cluster = 1

        # get how many test required
        self.num_test = num_test
        print(f"self.num_test = {self.num_test}", flush=True)

        # getting current folder
        self.current_directory = os.getcwd()
        print(f"self.current_directory = {self.current_directory}", flush=True)

        # getting folder (random or cluster)
        self.topology_folder = os.path.join(self.current_directory, self.topology_folder_only)
        print(f"self.topology_folder = {self.topology_folder}", flush=True)

        # list of files to test (from json filename)
        self.listOfFiles = self.getListofFiles(self.topology_folder)
        print(f"self.listOfFiles = {self.listOfFiles}", flush=True)

    def getListofFiles(self,directory):
        """
        Returns a list of nodes (json files) total for a given directory
        """
        try:
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        except FileNotFoundError:
            print(f"Directory not found: {directory}",flush=True)
            return []

    def getTotalNodes(self,filename):
        """
        Returns of nodes total for a given filename
        Example : nodes11_Dec2820242230.json, will return 10
        """
        try:
            match = re.search(r"nodes(\d+)_", filename)  # Use regex to find the number
            if match:
                return int(match.group(1))  # Extract the captured number and convert to integer
        except FileExistsError:
            print(f"Filename {filename} do not exist", flush=True)
            return []

    def run_command(self,command, full_path=None):
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

            print(f"result.stdout: {result.stdout}",flush=True)
            print(f"result.stderr: {result.stderr}", flush=True)
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

    def wait_for_pods_to_be_ready(self,namespace='default', expected_pods=0, timeout=300):
        """
                Waits for all pods in the specified namespace to be down
                by checking every second until they are terminated or timeout is reached.
        """
        print(f"Checking for pods in namespace {namespace}...", flush=True)
        start_time = time.time()
        get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers | grep Running | wc -l"

        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(get_pods_cmd, shell=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Check for "No resources found" in the output
                # print(f"result {result}",flush=True)
                running_pods = int(result.stdout.strip())
                if running_pods >= expected_pods:
                    print(f"All {expected_pods} pods are up and running in namespace {namespace}.", flush=True)
                    return True  # Pods are down
                else:
                    print(f" {running_pods} pods are up for now in namespace {namespace}. Waiting...", flush=True)

            except subprocess.CalledProcessError as e:
                print(f"Error checking for pods: {e.stderr}", flush=True)
                return False  # An error occurred

            time.sleep(1)  # Check every second

        print(f"Timeout waiting for pods to terminate in namespace {namespace}.", flush=True)
        return False  # Timeout reached

    def wait_for_pods_to_be_down(self,namespace='default', timeout=300):
        """
        Waits for all pods in the specified namespace to be down
        by checking every second until they are terminated or timeout is reached.
        """
        print(f"Checking for pods in namespace {namespace}...", flush=True)
        start_time = time.time()
        # get_pods_cmd = f"kubectl get pods -n {namespace}"
        get_pods_cmd = f"kubectl get pods -n {namespace} --no-headers | grep Terminating | wc -l"

        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(get_pods_cmd, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)

                # Check for "No resources found" in the output
                # terminating_pods = int(result.stdout.strip())
                # print(f"result {result}",flush=True)
                if "No resources found" in result.stderr:
                    print(f"No pods found in namespace {namespace}.", flush=True)
                    return True  # Pods are down
                else:
                    print(f"Pods still exist in namespace {namespace}. Waiting...", flush=True)

            except subprocess.CalledProcessError as e:
                print(f"Error checking for pods: {e.stderr}", flush=True)
                return False  # An error occurred

            time.sleep(1)  # Check every second

        print(f"Timeout waiting for pods to terminate in namespace {namespace}.", flush=True)
        return False  # Timeout reached

    def access_pod_and_initiate_gossip(self,pod_name, filename, unique_id, iteration):
        try:
            session = subprocess.Popen(['kubectl', 'exec', '-it', pod_name, '--', 'sh'], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            message = f'{filename[:-5]}-{unique_id}-{iteration}'
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Usage: python automate.py --num_test <number_of_tests> --cluster <total_cluster>")
    parser.add_argument('--num_test', required=True, help="Total number of tests to do")
    parser.add_argument('--cluster', required=True, help="Cluster or Non-cluster")
    args = parser.parse_args()
    test = Test(int(args.num_test),args.cluster)

    # helm name is fixed
    statefulsetname = 'gossip-statefulset'

    # Initiate helm chart and start the test based on nodes
    for i, file in enumerate(test.listOfFiles):

        # Getting filename
        print(f"file={file}", flush=True)

        # Get total nodes from a filename
        node = test.getTotalNodes(file)
        print(f"node={node}", flush=True)

        # if node == 10 or node == 30:
        # if node == 50:
        if node == 10:
            if test.wait_for_pods_to_be_down(namespace='default',timeout=300):

                    # Apply helm
                    # helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug --set image.tag=v5 --set cluster=0
                    result = test.run_command(['helm', 'install', statefulsetname, 'chartw/', '--values',
                                               'chartw/values.yaml', '--debug', '--set','cluster=' + str(test.cluster), '--set',
                                                'totalNodes=' + str(node)]
                                              )
                    print(f"Helm {statefulsetname}: {file} started...", flush=True)

                    if test.wait_for_pods_to_be_ready(namespace='default', expected_pods=node, timeout=300):

                        # Create unique uuid for this test
                        unique_id = str(uuid.uuid4())[:4]  # Generate a UUID and take the first 4 characters

                        # Test iteration starts here
                        for nt in range(1, test.num_test + 1):

                            # Choosing gossip-statefulset-0 as initiator
                            # Can change this to random later
                            pod_name = "gossip-statefulset-0"
                            print(f"Selected pod for test {nt}: {pod_name}", flush=True)

                            # Start accessing the pods and initiate gossip
                            if test.access_pod_and_initiate_gossip(pod_name, file, unique_id, nt):
                                print(f"Test {nt} complete for {file}.", flush=True)
                            else:
                                print(f"Test {nt} failed for {file}.", flush=True)
                    else:
                        print(f"Failed to prepare pods for {file}.", flush=True)
                        continue

                    # Remove helm
                    result = test.run_command(['helm', 'uninstall', statefulsetname])
                    print(f"Helm {statefulsetname} will be uninstalled...", flush=True)
                    if test.wait_for_pods_to_be_down(namespace='default', timeout=300):
                        print(f"Helm {statefulsetname}: {file} uninstalled is completed...", flush=True)
