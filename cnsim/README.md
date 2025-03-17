# Cloud-Native Simulation Framework for Gossip Protocol: Modeling and Analyzing Network Dynamics
This code is for PLOS One article entitled *Cloud-Native Simulation Framework for Gossip Protocol: Modeling
and Analyzing Network Dynamics*.

**A guide to deploy and utilizing a cloud-native simulation framework for studying gossip protocol dynamics in distributed networks.**

## Simulator Overview
This simulator leverages Google Cloud Platform services to provide a scalable and flexible environment for modeling and analyzing gossip protocols. The architecture comprises:

* **Google Kubernetes Engine (GKE):** For deploying and managing the distributed network nodes, simulating gossip activity. GKE allows for easy scaling and management of the simulation environment.
* **Google BigQuery:** For storing and querying simulation data, enabling efficient data analysis. BigQuery's serverless architecture allows for fast and cost-effective analysis of large datasets.
* **Google Colab:** For data visualization and in-depth analysis of simulation results. Colab provides a free and accessible environment for Python-based data analysis.

## Implementation Steps

### Step 1: Topology Creation (Fully Connected Network)

The network topology is generated using `network_constructor.py`, employing a fully connected network model. This model ensures that every node can directly communicate with every other node, which is useful for initial testing of the gossip protocol. The script generates topology files (e.g., node neighbor lists) stored in the `topology` folder. These files detail which nodes are directly connected, crucial for the gossip protocol's message propagation.

```shell
# Generate a fully connected network with 10 nodes and save the topology
python network_constructor.py --nodes 10 --save
```
### Step 2 - Develop grpc communication protocol (using python3)
gRPC is used for inter-node communication, providing efficient and reliable message passing. gRPC is a high-performance Remote Procedure Call (RPC) framework that allows nodes to communicate as if they were calling local functions. The *gossip.proto* file defines the communication interface, specifying the message structure and service definitions. This file is then compiled into Python classes (*gossip_pb2.py*, *gossip_pb2_grpc.py*). These classes provide the necessary code for serializing and deserializing messages, and for implementing the gRPC server and client.

### Step 3: Gossip Script (Direct Mail Gossip)
The simulator implements a "Direct Mail Gossip" protocol, where nodes directly send messages to their neighbors. This is a basic form of gossip protocol, where each node maintains a list of its neighbors and forwards messages to them.

- *start.py* initiates the gossip process by sending a message to the node itself. This simulates a node originating a message.
- *node.py* acts as a gRPC server, receiving and propagating messages to neighboring nodes. It listens for incoming messages and, upon receipt, forwards them to the nodes listed in its neighbor list.
```shell
# Initiate gossip with the message "Hello, Gossip!" example
python start.py --message "Hello, Gossip!"
```

### Step 4: Docker Image Creation and Deployment
A Docker image (wwiras/cnsim:v1) is built by running the docker build command at *cnsim* root folder and pushing it to Docker Hub. This will enable easy deployment on GKE.
```
docker build -t wwiras/cnsim:v1 .
docker push wwiras/cnsim:v1
```

### Introduction
Distributed networks, such as those used in IoT, blockchain, VANETs, and MANETs, are complex systems where 
efficient and reliable communication is critical. Gossip protocols, which allow nodes to share information 
in a decentralized and fault-tolerant way, are widely used in these environments but require careful research 
to improve scalability and durability. To address this, we have developed a cloud-native simulator that mimics 
gossip protocols in distributed networks. This simulator provides a flexible platform to study and optimize 
communication strategies, helping researchers tackle challenges like dynamic topologies, node mobility, 
and resource constraints. By enabling large-scale simulations, our tool aims to advance the development 
of robust and scalable distributed systems.

### Simulator Platform 
This simulator platform is consists of:-
- Google Kubernetes Engine (in Google Cloud Platform) - Gossip activity simulation
- Google BigQuery - Data collection and extraction
- Google Colab - Data analisys and virtualization 

### Steps to implement

#### Step 1 - Build topology using fully conneceted network model
Topology is created (using network_constructor.py) with Full connected network model. 
All topology files are saved in topology folder. 

```shell
# Full connected network (with total_node and save indicator inputs)
python network_constructor.py --nodes 10 --save 
```

#### Step 2 - Develop grpc communication protocol (using python3)
This simulator uses grpc for communication between pods. *gossip.proto* file 
is created and compile to produce *gossip_pb2.py* and *gossip_pb2_grpc.py*.

#### Step 3 - Develop gossip script (Direct Mail Gossip) 
Two files are created using python3.
- start.py : to initiate gossip by sending a message from the pod's itself
- node.py : build a grpc server to receive and propagate message (to it's neighbor - from Step 1)

```shell
# initiate gossip by sending message to himself (self triggered)
python start.py --message any_message
```

#### Step 4 - Build docker image and upload to docker hub
Build docker images based on cnsim script (from the root folder) and push it to docker hub. 
```
docker build -t wwiras/cnsim:v1 .
docker push wwiras/cnsim:v1
```

#### Step 5 - Deployment and gossip test
Below are the steps to deploy and initialize gossip (together with helm uninstall) manually. 

a. Helm chart is used to deploy our *Statefulset*. 
```shell 
helm install gossip-statefulset ./chartsim --set testType=default,totalNodes=10
```
<small> Note: Refer values.yaml in chartsim directory to see what values can be customized.</small>

b. Once *Statefulset* is ready, access any pod to execute gossip initialization by sending 
a message to himself (command in Step 3). 
```shell
# Access pod gossip-statefulset-0  
kubectl exec -it gossip-statefulset-0 -- sh
```

After this, a message is send from the initialize pod to its neighbors. From there, its neighbor, 
will send the received message to their neighbors. This process will continue until all pods receive 
this message including new and duplicated message. Through *fluentd* agent on each pod, all this 
activities will be recorded and stored to google cloud logging.

c. Once propagation (gossip) is completed, exit pod and run helm uninstall command to remove 
*Statefulset* deployment.
```shell 
helm uninstall gossip-statefulset
```

Fortunately, a python script has been developed (*automate_all.py*) to automate and simplify all this tasks. 
Refer code for more details.
```shell
# gossip automation script
python automate_all.py --num_nodes 10 --num_tests 10
```

#### Step 6 - Data collection and extraction

#### Step 7 - Data analysis
