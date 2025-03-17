## Cloud-Native Simulation Framework for Gossip Protocol: Modeling and Analyzing Network Dynamics
This code is for PLOS One article entitled *Cloud-Native Simulation Framework for Gossip Protocol: Modeling
and Analyzing Network Dynamics*.

**A guide to deploy and utilizing a cloud-native simulation framework for studying gossip protocol dynamics in distributed networks.**

### Simulator Overview
This simulator leverages Google Cloud Platform services to provide a scalable and flexible environment for modeling and analyzing gossip protocols. The architecture comprises:

* **Google Kubernetes Engine (GKE):** For deploying and managing the distributed network nodes, simulating gossip activity. GKE allows for easy scaling and management of the simulation environment.
* **Google BigQuery:** For storing and querying simulation data, enabling efficient data analysis. BigQuery's serverless architecture allows for fast and cost-effective analysis of large datasets.
* **Google Colab:** For data visualization and in-depth analysis of simulation results. Colab provides a free and accessible environment for Python-based data analysis.

### Implementation Steps

#### Step 1: Topology Creation (Fully Connected Network)

The network topology is generated using `network_constructor.py`, employing a fully connected network model. This model ensures that every node can directly communicate with every other node. The script generates topology files (e.g., node neighbor lists) stored in the `topology` folder.

```shell
# Generate a fully connected network with 10 nodes and save the topology
python network_constructor.py --nodes 10 --save
```
#### Step 2 - Develop grpc communication protocol (using python3)
gRPC is used for inter-node communication, providing efficient and reliable message passing. gRPC is a high-performance Remote Procedure Call (RPC) framework that allows nodes to communicate as if they were calling local functions. The *gossip.proto* file defines the communication interface, specifying the message structure and service definitions. This file is then compiled into Python classes (*gossip_pb2.py*, *gossip_pb2_grpc.py*). These classes provide the necessary code for serializing and deserializing messages, and for implementing the gRPC server and client.

#### Step 3: Gossip Script (Direct Mail Gossip)
The simulator implements a "Direct Mail Gossip" protocol, where nodes directly send messages to their neighbors. This is a basic form of gossip protocol, where each node maintains a list of its neighbors and forwards messages to them.

- *start.py* initiates the gossip process by sending a message to the node itself. This simulates a node originating a message.
- *node.py* acts as a gRPC server, receiving and propagating messages to neighboring nodes. It listens for incoming messages and, upon receipt, forwards them to the nodes listed in its neighbor list.
```shell
# Initiate gossip with the message "Hello, Gossip!" example
python start.py --message "Hello, Gossip!"
```

#### Step 4: Docker Image Creation and Deployment
A Docker image (wwiras/cnsim:v1) is built by running the docker build command at *cnsim* root folder and pushing it to Docker Hub. This will ease deployment on GKE.
```
docker build -t wwiras/cnsim:v1 .
docker push wwiras/cnsim:v1
```
#### Step 5: GKE Deployment and Gossip Test
The *automate_all.py* script automates the deployment (using *helm install* command) of the simulator on GKE using a StatefulSet. Once StatefulSets are ready, gossip will initiated by one pod to its neigbor and so on. During this gossip, *fluentd* collects logs from each pod and sends them to Google Cloud Logging.  After the simulation completed, the *helm uninstall* command is executed to bring down all statefulsets. Refer automate_all.py script for more detail.
```shell
# gossip automation script
python automate_all.py --num_nodes 10 --num_tests 10
```

#### Step 6: Data Collection and Extraction
All logs that are filtered by the message content of the gossip will be used in Google BigQuery. Prerequisite of this step to create a "sink" in Google Cloud Logging so that filtered logs will be routed to a BigQuery dataset.

#### Step 7: Data Analysis
All logs from the gossip activities will be used in Google BigQuery. Prerequisite of this step to create a sink in Google Cloud Logging that will route the logs to a BigQuery dataset. From there, new datasets (.csv format) will be created for data analysis. 

#### Step 8: Data Analysis
*.csv files that have been created from the previous step (Step #7) are then loaded to Google Colab for data analysis and virtualization. 

