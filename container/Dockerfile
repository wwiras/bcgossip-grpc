# Use an official Python runtime as a parent image
#FROM python:3.10.11-slim
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir grpcio grpcio-tools

# Make port 5050 available to the world outside this container
EXPOSE 5050

# Run node.py when the container launches
CMD ["python", "node.py"]
# The CMD is commented out because you'll likely want to specify the node_id and port dynamically

