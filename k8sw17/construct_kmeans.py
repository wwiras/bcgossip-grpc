import networkx as nx
import os
import json
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
import argparse
import time
from timeit import default_timer as timer

start_timer = 0
end_timer = 0

def check_inter_clusters(G,cluster_members):
    """
        This is optional. It will check whether inter clusters
        are connected or not.

        Input: G - NetworkX graph (existing topology - BA/ER)
        cluster_members - list of members of the clusters (with its cluser id)

        Returns: True if the clusters are connected, False otherwise
    """
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

def inter_clusters_connectors(G, cluster_members):
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

def intra_clusters_connectors(graph,newgraph,centroid_nodes):
    """
        Input:
        a. graph - networkx graph from BA/ER model
        b. newgraph - networkx graph with fully inter cluster connected components
        b. centroid - list of centroid cluster members (from each cluster)

        Return :
        If newgraph is fully connected, return it
        If newgraph is not fully connected, return False

        If inter clusters and intra clusters are successfully connected,
        a newly networkx graph will be created and returned
    """
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

def create_cluster_graph(graph,cluster_members):
    """
    Input:
    a. graph - a networkx graph (empty)
    b. cluster_members - Cluster with inter cluster
    are connected

    Return : graph - a networkx graph with cluster members content

    If inter clusters and intra clusters are successfully connected,
    a newly networkx graph will be created and returned
    """

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

def display_new_topology(cluster_members,newgraph):
    """
    Displays the new topology with colored clusters and centroid indicators.
    """
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

def save_new_topology(gnewgraph, filename, k, end_time, clusters):
    """
    Saves the topology to a JSON file with date and time in the filename.
    It will store details about the cluster
    a. time to complete the cluster (ms)
    b. number of clusters

    Input:
    a. gnewgraph: networkx graph (newly created)
    b. filename: topology json filename (BA/ER) network
    c. k: number of clusters
    d. end_time: total time to construct cluster (ms)
    e. clusters: list of clusters (fixed member cluster)

    Return: None (newly kmeans topology will be saved)
    at "topology_kmeans" directory
    """
    # Create directory if it doesn't exist
    output_dir = "topology_kmeans"
    os.makedirs(output_dir, exist_ok=True)

    # Construct the full file path
    fileout = f"kmeans_{filename[:-5]}_k{k}.json"
    file_path = os.path.join(output_dir, fileout)

    # Convert the graph to a JSON-serializable format with cluster labels
    # add nodes to graph
    nodes =[]
    for clusterid, cluster in enumerate(clusters):
        for node in cluster:
            nodes.append({'id':node, 'cluster': clusterid})
    # nodes = [{'id': node, 'cluster': clusters[i]} for i, node in enumerate(clusters)]
    # print(f"nodes={nodes}")

    # add edges to graph
    edges = [{'source': source, 'target': target, 'weight': data['weight']}
             for source, target, data in gnewgraph.edges(data=True)]

    # Include 'directed', 'multigraph', and 'graph'
    graph_data = {
        'directed': False,
        'multigraph': False,
        'total_clusters': k,
        # Add clustering time as a comment (disabled by default)
        'total_clustering_time_ms': end_time,
        'graph': {},
        'nodes': nodes,
        'edges': edges
    }

    # Save the topology
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, indent=4)


# Main code
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Choose options.")
    parser.add_argument('--cluster', type=int, default=2, help="How many clusters to create")
    # Add the optional argument with a default value of False
    parser.add_argument('--display', action='store_true', help="Display new topology (default: False)")
    parser.add_argument('--save', action='store_true', help="Save new topology to json(default: False)")
    args = parser.parse_args()

    # k = total clusters
    k=int((args.cluster))

    # select filename manually from here. Easy to remember with manual
    # filename = "nodes10_Jan102025104552_ER0.1.json"
    # filename = "nodes10_Jan102025113639_BA5.json"
    # filename = "nodes30_Jan102025113707_BA5.json"
    # filename = "nodes30_Jan102025113830_ER0.1.json"
    # filename = "nodes50_Jan082025181240_BA5.json"
    # filename = "nodes50_Jan082025181429_ER0.1.json"
    # filename = "nodes70_Jan082025004519_BA5.json"
    # filename = "nodes70_Jan082025201400_ER0.1.json"
    # filename = "nodes100_Jan082025004526_BA5.json"
    filename = "nodes100_Jan082025201753_ER0.1.json"

    # Get the current working directory
    current_directory = os.getcwd()

    # Construct the full path to the topology folder
    topology_folder = os.path.join(current_directory, "topology")

    # Load data from the JSON file
    print(f"filename = {filename}")
    with open(os.path.join(topology_folder,filename), 'r') as f:  # Use self.filename
        data = json.load(f)

    # Build graph from json (existing topology)
    G = nx.Graph()
    for node in data['nodes']:
        # print(f"node['id']:{node['id']}")
        G.add_node(node['id'])
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])

    # Confirm that the topology is connected
    print(f"From {filename} topology, is it all connected? (nx.is_connected(G)): {nx.is_connected(G)} and \n The graph info is G:{G}")
    print(f'total clusters: {k}')
    # Get number of nodes
    num_nodes = len(data['nodes'])

    # Kmeans construction time
    # a. distance matrix
    # b. kMeans fitting
    # c. get centroid neighbors and cluster members
    # d. fix cluster members connection (inter cluster)
    # e. fix intra cluster connection
    start_kmeans_time = time.time()
    start_timer = timer()

    # Calculate the distances matrix from json topology
    distance_matrix = dict(nx.all_pairs_dijkstra_path_length(G))
    distances = [[distance_matrix[n1][n2] for n2 in G.nodes] for n1 in G.nodes]
    # print(f"Distances Matrix:\n {distances}")

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
    kmeans.fit(distances)

    # kmeans fitting time
    kmeans_fitting_time = time.time()

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
    # print(f'Kmeans clustering, centroid_nodes: {centroid_nodes}')

    # Create a list to store the nodes in each cluster and cluster details
    cluster_members = [[] for _ in range(k)]
    for i, label in enumerate(labels):
        cluster_members[label].append(list(G.nodes)[i])
    # print(f'Kmeans clustering, cluster_members: {cluster_members}')

    # Check whether all clusters connected or not
    # all_clusters_connected = check_inter_clusters(G, cluster_members)
    # print(f'all_clusters_connected:{all_clusters_connected}')

    # Check and fix inter cluster connectors
    fixed_members = inter_clusters_connectors(G, cluster_members)
    if fixed_members: # if inter cluster connection can be established, return fix cluster members

        print(f'All inter clusters are connected !')
        # print(f'All inter clusters are connected \n fix_members: {fixed_members}')

        # Construct new graph
        newG = create_cluster_graph(G, fixed_members)

        # Connect intra clusters
        newG = intra_clusters_connectors(G, newG, centroid_nodes)

        if not newG: # If intra cluster connection cannot be established, return False
            print(f'Sorry! {filename} topolgy unable to connect intra cluster using kMeans with (cluster={k}).')
        else: # If intra cluster can be established, return updated new graphs with intra cluster connectors

            # total cluster kmeans time
            end_time_all = (time.time() - start_kmeans_time) * 1000  # Calculate time in milliseconds
            end_time_ms = "{:.5f}".format(end_time_all)
            end_timer = timer()

            # Print all info required
            print(f'Total clustering time (ms) : {end_time_ms}')
            # print(f'Total clustering time (ms) with timer : {(end_timer - start_timer)}')
            print(f'newG: {newG}')
            print(f'Is newG is connected (nx.is_connected(newG)): {nx.is_connected(newG)}')

            # display kmeans topology
            if args.display:
                display_new_topology(fixed_members, newG)

            # save kmeans topology
            if args.save:
                save_new_topology(newG, filename, k, end_time_ms,fixed_members)
                # save_new_topology(gnewgraph, filename, k, end_time, cluster_members)

    else: # If inter cluster can be established, return False
        print(f'Sorry! {filename} topolgy unable to connect inter cluster using kMeans (cluster={k})')
