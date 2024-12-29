import os
import argparse
import re
import subprocess
import sys

class Test:
    def __init__(self,num_test,cluster):

        # Getting topology folder
        # 0 - for non cluster, 1 - for cluster topology
        if cluster == '0':
            topology_folder = 'topology'
        else:
            topology_folder = 'topology_kmeans'

        # get how many test required
        self.num_test = num_test
        print(f"self.num_test = {self.num_test}", flush=True)

        # getting current folder
        self.current_directory = os.getcwd()
        print(f"self.current_directory = {self.current_directory}", flush=True)

        # getting folder (random or cluster)
        self.topology_folder = topology_folder
        print(f"self.topology_folder = {self.topology_folder}", flush=True)

        # list of nodes to test (from json filename)
        self.nodes = self.getListofNodes(os.path.join(self.current_directory, topology_folder))
        print(f"self.nodes = {self.nodes}", flush=True)

        # List all files in the directory and filter out subdirectories
        # deployment_files = [f for f in os.listdir(os.path.join(self.current_directory, topology_folder)) if os.path.isfile(os.path.join(deployment_path, f))]
        # print(f"deployment_files = {deployment_files}", flush=True)

        # Split the path string by the OS-specific separator
        # folders = self.current_directory.split(os.sep)
        # print(f"folders = {folders}", flush=True)


    def getListofNodes(self,directory):
        """
        Returns a list of nodes total for a given directory
        """
        try:
            listoffiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            # print(f"listoffiles = {listoffiles}", flush=True)
            nodes = []
            for file in listoffiles:
                match = re.search(r"nodes(\d+)_", file)  # Use regex to find the number
                if match:
                    nodes.append(int(match.group(1)))   # Extract the captured number and convert to integer
            return nodes
        except FileNotFoundError:
            print(f"Directory not found: {directory}",flush=True)
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
    parser = argparse.ArgumentParser(description="Usage: python automate.py --num_test <number_of_tests> --cluster <total_cluster>")
    parser.add_argument('--num_test', required=True, help="Total number of tests to do")
    parser.add_argument('--cluster', required=True, help="Cluster or Non-cluster")
    args = parser.parse_args()
    test = Test(int(args.num_test),args.cluster)

    # Initiate and Remove cluster based on nodes
    for i,node in enumerate(test.getListofNodes(test.topology_folder)):

        # print(f"index:{i} node:{node}", flush=True)
        test.run_command(['kubectl', 'version'])

        # Apply helm statefulset
        if i == 0:
            print(i,flush=True)
            break


        # break
