# import os

# Before running this script in the terminal, make sure
# a. Cluster instance is running (based on the specifications of the test)
# b. Enter the terminal through web google cloud terminal
# c. git pull (getting the latest code)
# d. you are ready to run this script


# 1. Set the service
# os.system('kubectl apply -f /home/puluncode/bcgossip-grpc/k8sv2/svc-bcgossip.yaml')
# try:
#     command = 'kubectl apply -f /home/puluncode/bcgossip-grpc/k8sv2/svc-bcgossip.yaml'
#
#     # Capture the output of the command using subprocess
#     result = os.popen(command).read()
#
#     if 'unchanged' or 'created' in result:
#         print("bcgossip is ready!")
#
# except:
#         print 'Error'
#         traceback.print_exc()
#         sys.exit(1)
#
# # Print the result
# print("Output from command:", result)
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


def deploy_application():
    command = ['kubectl', 'apply', '-f', '/home/puluncode/bcgossip-grpc/k8sv2/svc-bcgossip.yaml']

    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        # Check if the deployment was successful
        if 'unchanged' in result.stdout or 'created' in result.stdout:
            print("bcgossip is ready!")
        else:
            print("Deployment updated or other changes applied.")
            print(result.stdout)

    except subprocess.CalledProcessError as e:
        # Handle errors that result in a non-zero exit code
        print("An error occurred while applying the deployment.")
        print(f"Error message: {e.stderr}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        # Handle other exceptions
        print("An unexpected error occurred.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    deploy_application()

#!/usr/bin/env python3
#
# import subprocess
#
# try:
#     ls = subprocess.run( ("ls", "-w"), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
#     ls.check_returncode()
# except subprocess.CalledProcessError as e:
#     print ( "Error:\nreturn code: ", e.returncode, "\nOutput: ", e.stderr.decode("utf-8") )
#     raise
#
# print ( ls.stdout.decode("utf-8") )