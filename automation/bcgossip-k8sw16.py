import os
import sys

def main(num_tests, deployment_folder):
    # base directory of our main gossip folder path
    base_dir = "/home/wwiras/bcgossip-grpc/"
    print(f"base_dir = {base_dir}", flush=True)

    # deployment folder path
    deployment_path = os.path.join(base_dir, deployment_folder)
    print(f"deployment_path = {deployment_path}", flush=True)

    # root folder (k8swx folder) path
    root_folder = "/".join(deployment_path.split("/")[:-2])
    print(f"root_folder = {root_folder}", flush=True)

     # Ensure the path provided is actually a directory
    if not os.path.isdir(deployment_path):
        print(f"Error: The provided path {deployment_path} is not a directory.", flush=True)
        sys.exit(1)

    # List all files in the directory and filter out subdirectories
    deployment_files = [f for f in os.listdir(deployment_path) if os.path.isfile(os.path.join(deployment_path, f))]

    # Check if deployment files found or not
    if not deployment_files:
        print("No deployment files found in the directory.")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python bcgossip-k8sw16.py <number_of_tests> <deployment_folder>")
        sys.exit(1)
    num_tests = int(sys.argv[1])
    deployment_folder = sys.argv[2]
    result = main(num_tests, deployment_folder)