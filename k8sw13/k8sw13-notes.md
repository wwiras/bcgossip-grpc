## Notes on kMeans BCGP (BlockChain Gossip Protocol)

### Introduction
This k8sw13 is a folder where the random gossip algorithm happens
with the construction of k-Means cluster. Options for kMeans clustering.

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
to implement it.

### Steps to implement KMeans Clustering

1. Create a random json topology (all are connected - basic P2P) together 
with the latency and put it in topology folder.

```shell
# Please use ntgraph3.py to create this random json topology
python ntgraph3.py --nodes 10 --prob 3.0
```

```shell
# Please use ntgraph3.py to create json topology with fix 30 ms latency for all
python ntgraph3.py --nodes 10 --prob 3.0 --latency 30
```
A json file (containing a graph topology) will be generated. 
To view it (optional), use command below.
```shell
# Viewing json topology with latency
python ptgraphLT.py --filename nt_nodes10_p3.0_RL_c1121.json
```

2. Read the file with the input and runs kMeans to get new topolgy
```shell
# To run the code and display or save new topology (display=True) and (save=True):
python convert_kmeans.py --filename nt_nodes10_p3.0_RL_c1121.json --num_cluster 2 --display --save
    
#To run the code and ignore display and save new topology (display=False)and (save=False):
python convert_kmeans.py --filename nt_nodes10_p3.0_RL_c1121.json --num_cluster 2
```

3. Once new topology obtained, run the distributed system 
based on that (bringing up the kubernetes environment).
