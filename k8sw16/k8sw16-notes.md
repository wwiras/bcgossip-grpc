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
1. Build random topology (input: nodes,n) using leptokurtic latency
2. Build cluster topology (input; k=total_cluster, json_file=from 1.)
3. Create docker image that will check env variable. If cluster==0, use topology folder 
and if cluster==1, use kmeans_topology folder 


#### Step 1 - Build random topology (input: nodes,n) using leptokurtic latency
Before initializing gossip, we need to create a topology that will
gossip with leptokurtic latency (range 2ms - 100ms) and mean of 10ms

```shell
python create_topology.py --nodes 10
```

This script will create a topology file with the latency required. However,
we cannot imagine the topology. Below is the script (command) to display
the topology

```shell
topology % python ../ptgraphLT.py --filename nt_nodes10_Dec2820240043.json 
```

#### Step 2 - Build cluster topology (input; k=total_cluster, json_file=from step 1)
This is an offline solution for a distribution system. Based on the output from step 1, we will create
anew topology (or graph network) with k cluster (from the argument of the command). To get track
on the files generated, we will save the cluster file based on the topology file (from step 1).
If the input filename is "nt_nodes10_Dec2820240043.json", the output is "kmeans_nodes10_Dec2820240043.json"
in topology_kmeans folder.

```shell
# To run the code and display or save new topology (display=True) and (save=True):
python convert_kmeans.py --filename nt_nodes10_Dec2820240043.json --num_cluster 2 --display --save
# the output file will kmeans_k2_nodes10_Dec2820240043.json
    
#To run the code and ignore display and save new topology (display=False)and (save=False):
python convert_kmeans.py --filename nt_nodes10_Dec2820240043.json --num_cluster 2
```




