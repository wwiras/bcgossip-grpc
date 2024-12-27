## Notes on BCGP (BlockChain Gossip Protocol)

### Introduction
This k8sw16 is a folder where the random gossip algorithm happens
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
to implement it. This folder also taking into account of non-cluster topology.


### Steps to implement
1. Build random topology (input: nodes,n) using leptokurtic latency (range 10ms - 100ms)
2. Build cluster topology (input; k=total_cluster, json_file=from 1.)
3. Create docker image that will check env variable. If cluster==0, use topology folder 
and if cluster==1, use kmeans_topology folder 


