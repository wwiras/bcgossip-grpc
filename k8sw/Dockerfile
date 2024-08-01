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
