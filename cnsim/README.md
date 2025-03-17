# Cloud-Native Simulation Framework for Gossip Protocol: Modeling and Analyzing Network Dynamics
This code is for PLOS One article entitled *Cloud-Native Simulation Framework for Gossip Protocol: Modeling
and Analyzing Network Dynamics*.

## Notes on Simulator

### Introduction
Distributed networks, such as those used in IoT, blockchain, VANETs, and MANETs, are complex systems where 
efficient and reliable communication is critical. Gossip protocols, which allow nodes to share information 
in a decentralized and fault-tolerant way, are widely used in these environments but require careful research 
to improve scalability and durability. To address this, we have developed a cloud-native simulator that mimics 
gossip protocols in distributed networks. This simulator provides a flexible platform to study and optimize 
communication strategies, helping researchers tackle challenges like dynamic topologies, node mobility, 
and resource constraints. By enabling large-scale simulations, our tool aims to advance the development 
of robust and scalable distributed systems.

In this note, the platform of this simulator, prequisite and the steps to implement it will be listed as below. 

### Simulator Platform 
This simulator platform is consists of:-
- Google Kubernetes Engine (in Google Cloud Platform) - Gossip activity simulation
- Google BigQuery - Data collection and extraction
- Google Colab - Data analisys and virtualization 

### Steps to implement

#### Step 1 - Build topology using model Fully Conneceted Network Model
Topology is created (using network_constructor.py) with Full connected network model. 
All topology files are saved in topology folder. 

```shell
# For BA model
python network_constructor.py --nodes 10 --save 
```

#### Step 2 - Build cluster topology (input; k=total_cluster, json_file=from step 1)
This is an offline solution for a distribution system. Based on the output from step 1, we will create
anew topology (or graph network) with k cluster (from the argument of the command). To get track
on the files generated, we will save the cluster file based on the topology file (from step 1).
If the input filename is "nodes10_Dec2820240043.json", the output is "kmeans_nodes10_Dec2820240043.json"
in topology_kmeans folder.

```shell
# To run the code and display or save new topology (display=True) and (save=True):
python construct_kmeans.py --filename nodes10_Dec2820240043.json --num_cluster 2 --display --save
# the output file will kmeans_k2_nodes10_Dec2820240043.json
    
#To run the code and ignore display and save new topology (display=False)and (save=False):
python construct_kmeans.py --filename nodes10_Dec2820240043.json --num_cluster 2
```

#### Step 3 - Buidl docker image (k8sw17) and run cluster options

Build docker images based on the k8sw16 script. 
```
docker build -t wwiras/k8sw17:v1 .
docker push wwiras/k8sw17:v1
```

But this time statefulset.yaml template will add with **CLUSTER** environment variable. The logic is:-
- *os.environ['CLUSTER'] == 0*, choose "topology" folder
- *os.environ['CLUSTER'] == 1*, choose "topology_kmeans" folder
```
# no cluster - random gossip
helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug --set cluster=0
```
```
# kmeans cluster
helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug --set cluster=1
```

### Running Latency Test

- Basically, we will create topology (random or kmeans cluster) on Step 1 and 2. (10,30, 50, 70, 100 or any amount).
- All of these topologies will be stored in the container images.
- Let say we want to run latency test for 30 nodes of random gossip. the command is as below 
```shell
helm install gossip-statefulset chartw/ --values chartw/values.yaml --debug --set cluster=0 --set totalNodes=30
```
- To start or initiate the test, just proceed with the command
```shell
# Make sure all pods are runnning using kubernetes command or tool
# make sure all pods has running status
$ kubectl get pod

# access random pods
$ kubectl exec -it gossip-statefulset-0 -- sh

# run gossip initialization 
$ python3 start.py --message "any message" 
```

### Running Latency Automation Test
We will write the commands here

### Notes on working topology
nodes50_Jan082025181429_ER0.1.json, works for k2 and k4