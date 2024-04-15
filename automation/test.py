# sample using os comman
import os
os.system('pwd')
os.system('cd ~')
os.system('ls -la')

# sample using system()
stream = os.popen('ls -la')
output = stream.readlines()
print(output)

