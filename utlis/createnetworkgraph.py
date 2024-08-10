import networkx as nx
import json

G = nx.Graph()
# nodes = ['Node' + str(i) for i in range(1, 6)] # 6 nodes
nodes = ['gossip-statefulset-' + str(i) for i in range(0, 5)] # 6 nodes
G.add_nodes_from(nodes)

# Manually add edges here (e.g., G.add_edge('Node1', 'Node2'))
# G.add_edge('Node1', 'Node2', weight=0)
# G.add_edge('Node1', 'Node3', weight=0)
# G.add_edge('Node3', 'Node4', weight=0)
# G.add_edge('Node3', 'Node5', weight=0)
# G.add_edge('Node4', 'Node6', weight=0)

G.add_edge('gossip-statefulset-0', 'gossip-statefulset-1', weight=0)
G.add_edge('gossip-statefulset-0', 'gossip-statefulset-2', weight=0)
G.add_edge('gossip-statefulset-2', 'gossip-statefulset-3', weight=0)
G.add_edge('gossip-statefulset-2', 'gossip-statefulset-4', weight=0)
G.add_edge('gossip-statefulset-3', 'gossip-statefulset-5', weight=0)

topology = nx.node_link_data(G)
with open('network_topology2.json', 'w') as outfile:
    json.dump(topology, outfile)