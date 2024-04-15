# sample using os comman
import os
os.system('pwd')
os.system('cd ~')
os.system('ls -la')

# sample using system()
stream = os.popen('ls -la')
output = stream.readlines()
print(output)


# STORING THE COMMAND OUTPUT TO A VARIABLE
import subprocess
x = subprocess.run(['ls', '-la'])
print(x)
print(x.args)
print(x.returncode)
print(x.stdout)
print(x.stderr)
