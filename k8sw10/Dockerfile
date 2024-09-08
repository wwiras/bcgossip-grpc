FROM ubuntu:22.04

WORKDIR /app

# Install required packages for Python
RUN apt-get update && apt-get install -y python3 python3-pip build-essential wget

# Install network utils
RUN apt-get install -y iputils-ping dnsutils iproute2 iperf3

# Install Python and necessary packages
RUN pip3 install --no-cache-dir grpcio grpcio-tools kubernetes iperf3 grpcio-reflection

# Copy your application source code
COPY src /app

# Expose the port the app runs on (if applicable)
EXPOSE 5050

# Command to run the application
CMD ["python3", "node.py"]



## Start with python slim image
#FROM python:3.11-slim
#
## Set the working directory in the container
## Copy the application source code to the container
#WORKDIR /app
#COPY . /app
#
## Install Python and necessary packages
#RUN pip install --no-cache-dir grpcio grpcio-tools kubernetes
##RUN pip install --no-cache-dir grpcio grpcio-tools kubernetes pandas-gbq asyncio
#
## Expose the port the app runs on
#EXPOSE 5050
#
## Command to run the application
#CMD ["python", "node.py"]

# For grpc compiler
# python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. gossip2.proto

# For GKE Big Query key
#kubectl create secret generic gossip-simulator-key --from-file=key.json=bcgossip.json

# For configmap
#kubectl create configmap topology-config --from-file=network_topology.json

