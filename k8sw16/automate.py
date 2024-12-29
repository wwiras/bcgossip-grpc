import os
import argparse
import re
import subprocess
import sys
import traceback

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

        # List all files in the directory and filter out subdirectories
        # deployment_files = [f for f in os.listdir(os.path.join(self.current_directory, topology_folder)) if os.path.isfile(os.path.join(deployment_path, f))]
        # print(f"deployment_files = {deployment_files}", flush=True)

        # Split the path string by the OS-specific separator
        # folders = self.current_directory.split(os.sep)
        # print(f"folders = {folders}", flush=True)


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
        Example : nodes10_Dec2820242230.json, will return 10
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Usage: python automate.py --num_test <number_of_tests> --cluster <total_cluster>")
    parser.add_argument('--num_test', required=True, help="Total number of tests to do")
    parser.add_argument('--cluster', required=True, help="Cluster or Non-cluster")
    args = parser.parse_args()
    test = Test(int(args.num_test),args.cluster)

    # Initiate helm chart and start the test based on nodes
    for i,file in enumerate(test.listOfFiles):

        # Get total nodes from a filename
        node = test.getTotalNodes(file)

        if node == 10:
            result = test.run_command(['kubectl', 'get','pod'])
            print(f"result={result}",flush=True)
            if "No resources found in default namespace.\n" in result:
                print(f"No resources. Can proceed Helm deployment",flush=True)

                # Apply helm
                # helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug --set image.tag=v5 --set cluster=0
                result = test.run_command(['helm', 'install', 'gossip-statefulset','chartw/','--values',
                                           'chartw/values.yaml', '--debug', '--set',
                                           'cluster='+str(test.cluster)])

                if wait_for_pods_to_be_ready(namespace='default', expected_pods=node, timeout=300):
                    print(f"You are good to go...", flush=True)
                else:
                    print(f"Failed to prepare pods for {test.topology_folder}.", flush=True)

            else:
                print(f"Something wrong here. Can't proceed Helm deployment", flush=True)
            break
