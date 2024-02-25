# Start with python slim image
FROM python:3.11-slim

# Set the working directory in the container
# Copy the application source code to the container
WORKDIR /app
COPY . /app

# Install Python and necessary packages
RUN pip install --no-cache-dir grpcio grpcio-tools kubernetes

# Expose the port the app runs on
EXPOSE 5050

# Command to run the application
CMD ["python", "node.py"]


## Start with Alpine Linux base image
#FROM alpine:3
#
## Install Python and necessary packages
#RUN apk add --no-cache python3 py3-pip py3-kubernetes iputils && \
#    pip3 install --upgrade pip && \
#    pip3 install grpcio grpcio-tools
#
## Set the working directory in the container
#WORKDIR /app
#
## Copy the application source code to the container
#COPY . /app
#
## Expose the port the app runs on
#EXPOSE 5050
#
## Command to run the application
#CMD ["python3", "node.py"]
