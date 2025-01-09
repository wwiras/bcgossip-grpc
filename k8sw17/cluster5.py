import networkx as nx
import os
import json
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

def check_cluster_connectivity(G,cluster_members):
    all_cluster_connected = True
    # Check connectivity within each cluster
    for cluster_id, members in enumerate(cluster_members):
        subgraph = G.subgraph(members)
        if nx.is_connected(subgraph):
            print(f"Cluster {cluster_id} is connected.")
        else:
            all_cluster_connected = False
            print(f"Cluster {cluster_id} is NOT connected.")
            # You can further analyze the disconnected components within the cluster
            for component in nx.connected_components(subgraph):
                print(f"  - Component: {component}")

    return all_cluster_connected

def ensure_connected_clusters(G, cluster_members):
    """
    Ensures all clusters are connected by moving disconnected components
    to the nearest cluster. Checks subgraph connectivity before assigning
    to the new cluster and verifies the entire graph's connectivity.
    Returns False if the final graph is not connected.

    Args:
        G (networkx.Graph): The original graph.
        cluster_members (list): List of cluster members.

    Returns:
        list or False: Updated list of cluster members with connected
                      clusters or False if the final graph is not connected.
    """

    for cluster_id, members in enumerate(cluster_members):
        subgraph = G.subgraph(members)
        if not nx.is_connected(subgraph):
            print(f"Cluster {cluster_id} is NOT connected. Finding nearest clusters for disconnected components...")
            components = list(nx.connected_components(subgraph))

            # Sort components by length in descending order
            components.sort(key=len, reverse=True)

            # a. Take the first longest component as the default cluster
            # base_component = components[0]

            # b. Find nearest clusters for the remaining components
            for i, component in enumerate(components[1:]):  # Start from the second component
                for node1 in component:
                    nearest_cluster_id = None
                    min_distance = float('inf')
                    for other_cluster_id, other_members in enumerate(cluster_members):
                        if other_cluster_id != cluster_id:
                            # Check if adding node1 to the other cluster creates a connected subgraph
                            temp_members = other_members + [node1]
                            temp_subgraph = G.subgraph(temp_members)
                            if nx.is_connected(temp_subgraph):
                                for node2 in other_members:
                                    if nx.has_path(G, node1, node2):
                                        distance = nx.shortest_path_length(G, source=node1, target=node2, weight='weight')
                                        if distance < min_distance:
                                            min_distance = distance
                                            nearest_cluster_id = other_cluster_id

                    if nearest_cluster_id is not None:
                        print(f"  - Moving {node1} from component {component} to nearest cluster {nearest_cluster_id} (distance: {min_distance})")
                        cluster_members[cluster_id].remove(node1)
                        cluster_members[nearest_cluster_id].append(node1)

    # Verify connectivity of the entire graph after processing all clusters
    print("RECHECK inter-cluster connection....")
    all_clusters_connected = True
    for clusterid, members in enumerate(cluster_members):
        temp_subgraph = G.subgraph(members)
        if nx.is_connected(temp_subgraph):
            print(f" Cluster {clusterid} is all connected.")
        else:
            all_clusters_connected = False
            print(f" Cluster {clusterid} is not connected.")

    if all_clusters_connected:
        return cluster_members
    else:
        return all_clusters_connected

# This is good enough but need to make sure the closest cluster
def fix_clusters_connection(G,cluster_members,disconnected_clusters):

    for cluster_id in disconnected_clusters:
        # get all members of the disconnected cluster
        members = cluster_members[cluster_id]
        print(f"Cluster ID: {cluster_id}")

        # merge them in to subgraph
        subgraph = G.subgraph(members)

        # get all components (that are isolated)
        components = list(nx.connected_components(subgraph))
        print(f"Components: {components}")

        # Get the longest component (the one with the most nodes)
        # longest_component = max(components, key=len)
        # print(f"longest_component: {longest_component}")

        # Take the first longest component as the default cluster
        # Sort components by length in descending order
        components.sort(key=len, reverse=True)
        base_component = components[0]
        print(f" base_component: {base_component}")

        # Find suitable clusters for the remaining components
        for i, component in enumerate(components[1:]):
            for node1 in component:
                for other_cluster_id, other_members in enumerate(cluster_members):
                    if other_cluster_id != cluster_id:
                        # Directly check if moving node1 creates a connected subgraph
                        temp_members = other_members + [node1]
                        temp_subgraph = G.subgraph(temp_members)
                        if nx.is_connected(temp_subgraph):
                            print(f"  - Moving {node1} from component {component} to cluster {other_cluster_id}")
                            cluster_members[cluster_id].remove(node1)
                            cluster_members[other_cluster_id].append(node1)
                            break  # Move to the next component
                        if node1 not in cluster_members[cluster_id]:
                            break  # Node has been moved, move to the next component
                if node1 not in cluster_members[cluster_id]:
                    break  # Node has been moved, move to the next component

    # Verify connectivity of the entire graph after processing all clusters
    all_cluster_nodes = set()
    for members in cluster_members:
        all_cluster_nodes.update(members)
    final_subgraph = G.subgraph(all_cluster_nodes)
    if nx.is_connected(final_subgraph):
        print("Final graph is connected.")
    else:
        print("WARNING: Final graph is NOT connected!")

    return cluster_members

def create_cluster_graph(graph,cluster_members):

    newgraph = nx.Graph()

    # Create nodes based on each cluster
    # print(f"cluster_members: {cluster_members}")
    # print(f"len(self.cluster_members): {len(self.cluster_members)}")
    for clusterid, nodes in enumerate(cluster_members):
        # print(f"clusterid:{clusterid},{nodes}")
        # Add nodes to new graph
        for node in nodes:
            newgraph.add_node(node)

        # Add edges to new graph nodes with weight
        # if self cluster by itself no need to add edges
        if len(nodes) > 1:
            for n1 in nodes:
                for n2 in nodes:
                    # ignore same nodes
                    if n1 == n2:
                        continue
                    else:
                        # Get edge data between nodes from previous graph
                        edge_data = graph.get_edge_data(n1, n2)
                        # if there is edge data from prev graph, get edge data
                        if edge_data is not None:
                            # if edge data not exist in new graph, add edge data
                            if not newgraph.get_edge_data(n1, n2):
                                newgraph.add_edge(n1, n2,weight=edge_data['weight'])
                                # print(f"New edge data between {n1} and {n2}: {edge_data} is added to new graph")
        print(f"newgraph:{newgraph}")

    print(f"nx.is_connected(newgraph) ? : {nx.is_connected(newgraph)}")
    return newgraph

def create_cluster_connectors(graph,newgraph,centroid_nodes):
    all_connected = False
    for cen in centroid_nodes:
        for cen_others in centroid_nodes:
            if not all_connected:
                if cen is not cen_others:

                    # Get shortest path (with node sequence)
                    shortest_path = nx.shortest_path(graph, source=cen, target=cen_others, weight='weight')
                    # print(f"nx.shortest_path(self.graph, source={cen}, target={cen_others}, weight='weight') \n {shortest_path}")

                    # Crawl or iterate through the shortest path
                    # Iterate up to the second-to-last element
                    for i in range(len(shortest_path ) - 1):
                        current_node = shortest_path [i]
                        next_node = shortest_path [i + 1]
                        # print(f'self.newgraph.get_edge_data({current_node}, {next_node}):{self.newgraph.get_edge_data(current_node, next_node)}')

                        # Check whether there is connection between
                        # two nodes in the path (crawler)
                        # If no edge (None). So add edge
                        if newgraph.get_edge_data(current_node, next_node) is None:
                            edge_data = graph.get_edge_data(current_node, next_node)
                            newgraph.add_edge(current_node, next_node, weight=edge_data['weight'])
                            # print(f'self.newgraph.get_edge_data({current_node},{next_node}):{self.newgraph.get_edge_data(current_node,next_node)}')

                            # Check new graph whether all nodes are connected
                            if nx.is_connected(newgraph):
                                all_connected = True
                                break
    if all_connected:
        return newgraph
    else:
        return all_connected

def display_new_topology(cluster_members,newgraph):
    """Displays the new topology with colored clusters and centroid indicators."""
    # Create a dictionary to map node to cluster
    node_to_cluster = {}
    for cluster_id, members in enumerate(cluster_members):
        for node in members:
            node_to_cluster[node] = cluster_id
    # print(f'node_to_cluster:\n {node_to_cluster}')

    # Get a list of node colors based on cluster assignment
    node_colors = [node_to_cluster[node] for node in newgraph.nodes()]

    # Get positions for nodes using a spring layout
    pos = nx.spring_layout(newgraph)

    # Draw the graph with colored nodes and edge labels
    nx.draw(newgraph, pos, with_labels=True, node_color=node_colors, cmap=plt.cm.viridis)
    labels = nx.get_edge_attributes(newgraph, 'weight')
    nx.draw_networkx_edge_labels(newgraph, pos, edge_labels=labels)

    plt.show()

# Get the current working directory
current_directory = os.getcwd()

# Construct the full path to the topology folder
topology_folder = os.path.join(current_directory, "topology")

# k = total clusters
k=3
# select filename
# filename = "nodes10_Jan062025154931_ER0.4.json"
filename = "nodes10_Jan062025154921_BA3.json"
# filename = "nodes30_Jan082025004502_BA5.json"
# filename = "nodes30_Jan082025004652_ER0.1.json"
# filename = "nodes50_Jan082025004511_BA5.json"
# filename = "nodes50_Jan082025181240_BA5.json"
# filename ="nodes50_Jan082025181429_ER0.1.json"
# filename ="nodes70_Jan082025004519_BA5.json"
# filename ="nodes70_Jan082025201400_ER0.1.json"
# filename ="nodes100_Jan082025004526_BA5.json"
# filename = "nodes100_Jan082025201753_ER0.1.json"


# Load data from the JSON file
print(f"filename = {filename}")
with open(os.path.join(topology_folder,filename), 'r') as f:  # Use self.filename
    data = json.load(f)

# Build graph (existing topology)
G = nx.Graph()
for node in data['nodes']:
    # print(f"node['id']:{node['id']}")
    G.add_node(node['id'])
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], weight=edge['weight'])

print(f"Topology from {filename} is connected nx.is_connected(G) ? : {nx.is_connected(G)} and G:{G}")

num_nodes = len(data['nodes'])

# Calculate the distances matrix
distance_matrix = dict(nx.all_pairs_dijkstra_path_length(G))
distances = [[distance_matrix[n1][n2] for n2 in G.nodes] for n1 in G.nodes]
# print(f"Distances Matrix:\n {distances}")

# 2. Apply K-means clustering
kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
kmeans.fit(distances)

# Get cluster labels and centroids
labels = kmeans.labels_
print(f'Kmeans clustering, labels: {labels}')

# Find the closest nodes to the centroids
centroids = kmeans.cluster_centers_
centroid_nodes = []
for centroid in centroids:
    # distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in self.weight_matrix]
    distances_to_centroid = [np.linalg.norm(np.array(row) - centroid) for row in distances]
    # print(f"distances_to_centroid: \n {distances_to_centroid}")
    closest_node_index = np.argmin(distances_to_centroid)
    # print(f"closest_node_index: \n {closest_node_index}")
    closest_node = list(G.nodes)[closest_node_index]
    # print(f"closest_node: \n {closest_node}")
    centroid_nodes.append(closest_node)

# Create a list to store the nodes in each cluster
cluster_members = [[] for _ in range(k)]
for i, label in enumerate(labels):
    cluster_members[label].append(list(G.nodes)[i])

# Cluster details
cluster_members = cluster_members
# print(f'Kmeans clustering, cluster_members: {cluster_members}')

centroid_nodes = centroid_nodes
print(f'Kmeans clustering, centroid_nodes: {centroid_nodes}')

all_clusters_connected = check_cluster_connectivity(G, cluster_members)
print(f'all_clusters_connected:{all_clusters_connected}')

# new_cluster_members = fix_clusters_connection(G,cluster_members,disconnected_clusters)
# print(f'new_cluster_members: {new_cluster_members}')

# Check and fix inter cluster connectors
fixed_members = ensure_connected_clusters(G, cluster_members)
if fixed_members: # if inter cluster connection can be established, return fix cluster members

    print(f'All inter clusters are connected !')
    # print(f'All inter clusters are connected \n fix_members: {fixed_members}')

    # Construct new graph
    newG = create_cluster_graph(G, fixed_members)

    # Connect intra clusters
    newG = create_cluster_connectors(G, newG, centroid_nodes)

    if not newG: # If intra cluster connection cannot be established, return False
        print(f'Sorry! {filename} topolgy unable to connect intra cluster using kMeans with (cluster={k}).')
    else: # If intra cluster can be established, return updated new graphs with intra cluster connectors
        print(f'newG: {newG}')
        print(f'total clusters: {k}')
        print(f'nx.is_connected(newG): {nx.is_connected(newG)}')
        display_new_topology(cluster_members, newG)
else: # If inter cluster can be established, return False
    print(f'Sorry! {filename} topolgy unable to connect inter cluster using kMeans (cluster={k})')


# Print the shortest path from node 0 to node 1
# print(f"nx.shortest_path(G, source=0, target=1, weight='weight') \n {nx.shortest_path(G,source='gossip-statefulset-0', target='gossip-statefulset-1', weight='weight')}")

# Print the shortest path from node 0 to all other nodes
# p = nx.shortest_path(G, source=0, weight='weight')
# print(f"nx.shortest_path(G, source=0, weight='weight') \n {p}")

