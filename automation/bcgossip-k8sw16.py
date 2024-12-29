import os
import argparse

class Test:
    def __init__(self,num_test,test_folder):

        # getting current folder
        self.current_directory = os.getcwd()
        print(f"self.current_directory = {self.current_directory}", flush=True)

        # Split the path string by the OS-specific separator
        folders = self.current_directory.split(os.sep)
        print(f"folders = {folders}", flush=True)

        # getting root folder
        root_folder = folders[:7]
        self.root_directory = os.sep.join(root_folder)
        print(f"self.root_directory = {self.root_directory}", flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Usage: python bcgossip-k8sw16.py --num_test <number_of_tests> --folder <deployment_folder>")
    parser.add_argument('--num_test', required=True, help="Total number of tests to do")
    parser.add_argument('--folder', required=True, help="Statefulset folder test")
    args = parser.parse_args()
    tests = Test()

