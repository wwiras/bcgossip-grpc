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
