import os

# Before running this script in the terminal, make sure
# a. Cluster instance is running (based on the specifications of the test)
# b. Enter the terminal through web google cloud terminal
# c. git pull (getting the latest code)
# d. you are ready to run this script


# 1. Set the service
os.system('kubectl apply -f /k8sv2/svc-bcgossip.yaml')

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


# sample using os comman
import os
os.system('pwd')
os.system('cd ~')
os.system('ls -la')

# sample using system()
stream = os.popen('ls -la')
output = stream.readlines()
print(f"output for system= {output}", flush=True)


# STORING THE COMMAND OUTPUT TO A VARIABLE
import subprocess
x = subprocess.run(['ls', '-la'], capture_output=True)
print(x)
print(x.args)
print(x.returncode)
print(x.stdout)
print(x.stderr)

