from datetime import datetime
import time
from timeit import default_timer as timer

start_time = datetime.now()

for i in range(10000):
    i ** 100

end_time = datetime.now()

time_difference = (end_time - start_time).total_seconds() * 10 ** 3
print("Execution time of program is: ", time_difference, "ms")

####
# Reference: https://www.programiz.com/python-programming/examples/elapsed-time
print("Using time module")
start = time.time()
print(f"start: {start}")
print(23*2.3)
# Save timestamp
end = time.time()
print(f"end: {end}")
print(f"(end - start): {(end - start)} ms \n")


print("Using timeit module")
start = timer()
print(f"start: {start}")
print(23*2.3)
end = timer()
print(f"end: {end}")
print(f"(end - start): {(end - start)} ms")
####