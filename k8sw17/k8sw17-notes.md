## Notes on DONS simulator - k8sw17

### Introduction
This purpose of k8sw17 folder is to create a simulator that will
imitate the simulation of "An Efficient Blockchain Neighbor Selection 
Framework Based on Agglomerative Clustering" paper. Basically, the based
of the network is based on DONS simulator 
(https://www.sciencedirect.com/science/article/pii/S0167739X2100491X)

#### Online KMeans Clustering
Consider this as "live" version. This is where the kMeans clustering is 
constructed within the distributed system. A node will be chosen 
as a leader node that will get all distributed systems node info like 
neighbor nodes together with weight variables (latency, bandwidth). 
Once obtained,  the node will execute the kMeans clustering and rebuild 
the topology (neighbor selection). This new topology will be distributed 
to all nodes for them to update.

#### Offline KMeans Clustering
In contrast, offline solution will construct the kMeans based on offline
distributed system. The scrip will get json file of the current topology
(and other information) and execute kMeans clustering. From that clustering
info, a new topology is created in json file. When the distributed system is
going to live, te newly created json file (kMeans clustering) will be used as
a reference.

In this solution so far we are using offline solution. Below are the steps
to implement it. This folder also taking into account of non-cluster topology.


### Steps to implement

#### Step 1 - Build random topology (input: nodes,n) using BA or ER model
BA = Barabási–Albert Network
ER = Erdös – Rényi(ER) Network
Before initializing gossip, we need to create a topology that will
gossip with BA or ER model latency (range 1ms - 100ms). Make sure
you provide save and display options (optional)

```shell
# For BA model
python network_constructor.py --nodes 7 --model BA --others 3 --save 
```

```shell
# For ER model
python network_constructor.py --nodes 7 --model ER --others 0.5 --display
```

This script will create a topology file (in topology folder) or 
display the topology based on the options provided.


#### Step 2 - Build cluster topology (input; k=total_cluster, json_file=from step 1)
This is an offline solution for a distribution system. Based on the output from step 1, we will create
anew topology (or graph network) with k cluster (from the argument of the command). To get track
on the files generated, we will save the cluster file based on the topology file (from step 1).
If the input filename is "nodes10_Dec2820240043.json", the output is "kmeans_nodes10_Dec2820240043.json"
in topology_kmeans folder.

```shell
# To run the code and display or save new topology (display=True) and (save=True):
python convert_kmeans.py --filename nodes10_Dec2820240043.json --num_cluster 2 --display --save
# the output file will kmeans_k2_nodes10_Dec2820240043.json
    
#To run the code and ignore display and save new topology (display=False)and (save=False):
python convert_kmeans.py --filename nodes10_Dec2820240043.json --num_cluster 2
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