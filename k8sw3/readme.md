# Kubernetes Gossip Protocol Simulation

This project simulates a gossip protocol in a Kubernetes cluster using gRPC for communication between pods. It utilizes a StatefulSet to manage the pods and a ConfigMap to define the network topology.

## Prerequisites

* **Kubernetes Cluster:**  You'll need a running Kubernetes cluster (Minikube, Kind, or a cloud-based cluster).
* **kubectl:**  Make sure you have `kubectl` installed and configured to interact with your cluster.
* **Protocol Buffers Compiler (protoc):** Install `protoc` to compile the `.proto` file. Follow the instructions for your operating system [here](https://grpc.io/docs/languages/python/quickstart/).
* **Python and Dependencies:**  Install Python and the required libraries:
    ```bash
    pip install grpcio grpcio-tools kubernetes
    ```

## Project Structure

* **`gossip.proto`:**  Defines the gRPC service and messages for the gossip protocol.
* **`node.py`:**  The main Python script that runs on each pod, handling message receiving, gossiping, and acknowledgment.
* **`start.py`:** A script to initiate the gossip process by sending a message to itself.
* **`gossip-statefulset.yaml`:**  The Kubernetes StatefulSet manifest to deploy the pods.
* **`svc-bcgossip.yaml`:**  The Kubernetes Service manifest to enable communication between pods.
* **`network_topology.json`:** (Optional) A JSON file defining the network topology if you want to use a ConfigMap for neighbor discovery.

## Setup

1. **Compile the Protocol Buffer Definitions**

   ```bash
   protoc --python_out=. --grpc_python_out=. gossip.proto 
