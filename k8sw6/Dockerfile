FROM ubuntu:22.04

WORKDIR /app

# Install required packages for Python
RUN apt-get update && apt-get install -y python3 python3-pip build-essential wget

# Install network utils including trickle
RUN apt-get install -y iputils-ping dnsutils iproute2 iperf3 trickle

# Install grpcurl (add this line)
RUN apt-get install -y grpcurl

# Install Python and necessary packages
RUN pip3 install --no-cache-dir grpcio grpcio-tools kubernetes iperf3

# Copy your application source code
COPY . /app

# Expose the port the app runs on (if applicable)
EXPOSE 5050

# Command to run the application
CMD ["python3", "node.py"]