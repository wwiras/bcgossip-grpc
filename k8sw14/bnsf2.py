import json
import os
import numpy as np
import argparse


class BNSF:
    def __init__(self, filepath, num_clusters):
        """
        Initializes a Node object with data from a JSON file and the desired number of clusters.

        Args:
          filepath: The path to the JSON file.
          num_clusters: The desired number of clusters.
        """
        with open(filepath, 'r') as f:
            self.data = json.load(f)
        self.num_clusters = num_clusters
        self.nodes = self.data['nodes']
        self.links = self.data['links']
        self.distance_matrix = None
        # self.AClusters = self.get_clusters(self.num_clusters)

    def get_total_nodes(self):
        """
        Returns the total number of nodes in the network.
        """
        return len(self.data['nodes'])

    def get_set_of_nodes(self):
        """
        Returns a set of node IDs in the network.
        """
        return {node['id'] for node in self.data['nodes']}

    def get_clusters(self):
        """
        Input : num_clusters: the desired number of clusters
        Returns : A list of clusters, where each cluster is a list of node IDs.
        """

        # 1. Create the distance matrix
        self.get_distance_matrix()
        print(f'distance matrix: \n {self.distance_matrix}',flush=True)

        # 2. Initialize clusters with each node as a separate cluster
        init_clusters = [[node['id']] for node in self.nodes]

        # 3. Create a mapping from node ID to index
        node_id_to_index = {node['id']: i for i, node in enumerate(self.nodes)}
        print(f'node_id_to_index: \n {node_id_to_index}', flush=True)

        # 3. Merge clusters iteratively

        # a. Cluster initialization
        clusters = init_clusters.copy()

        # b. Looping till required number of cluster achieved
        # while len(clusters) > self.num_clusters:

        # b. Find closest clusters:
        distance_matrix = self.distance_matrix
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):


                # Create a sub-matrix of distances between nodes in the two clusters
                # sub_matrix = distance_matrix[
                #     np.ix_([node_id_to_index[n] for n in clusters[i]],
                #            [node_id_to_index[n] for n in clusters[j]])
                # ]
                # dist = np.max(sub_matrix)  # Find the maximum distance (complete linkage)
                # print(f'dist :  {dist}')

                # print(f'sub_matrix:  {sub_matrix}', flush=True)

                # flat_index = np.argmin(sub_matrix)
                # Convert the flat index to row and column indices
                # row_index, col_index = np.unravel_index(flat_index, sub_matrix.shape)
                # print(f"minimum value from sub_matrix({row_index}, {col_index}): {sub_matrix[row_index, col_index]}")


                # cluster_i = clusters[i]
                # cluster_j = clusters[j]
                # distances = [
                #     self.distance_matrix[int(a.split('-')[-1]), int(b.split('-')[-1])]
                #     for a in cluster_i
                #     for b in cluster_j
                # ]
                # print(f'distances :  {distances}')
                print(f'clusters:  {clusters}')
                print(f'clusters[i]:  {clusters[i]}')
                print(f'clusters[j]:  {clusters[j]}')
                print(f'len(clusters[i]):  {len(clusters[i])}')
                print(f'len(clusters[j]:  {len(clusters[j])}')
                # clusters[i].append(clusters[j])
                clusters[i].extend(clusters[j])
                print(f'type clusters[i]:  {type(clusters[i])}')
                # clusters.remove(1)
                # del clusters[1]
                clusters.pop(1)
                clusters.pop(2)
                print(f'clusters[i]:  {clusters[i]}')
                print(f'clusters[j]:  {clusters[j]}')
                print(f'clusters:  {clusters}')
                clusters.pop(0)
                print(f'clusters:  {clusters}')
                break
            if i==0:
                break


        return clusters
        # return self.distance_matrix


    ### Create distance matrix global view
    def get_distance_matrix(self):
        num_nodes = len(self.nodes)
        dm = np.zeros((num_nodes, num_nodes))
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                source_id = self.nodes[i]['id']
                target_id = self.nodes[j]['id']
                latency = next((link['latency'] for link in self.links if
                                (link['source'] == source_id and link['target'] == target_id) or (
                                        link['source'] == target_id and link['target'] == source_id)), np.inf)
                dm[i, j] = dm[j, i] = latency

        self.distance_matrix = dm

if __name__ == '__main__':
    # Total number of clusters are given here
    parser = argparse.ArgumentParser(description='Perform BNSF on network nodes.')
    parser.add_argument('--num_clusters',required=True, type=int, help='Desired number of clusters.')
    args = parser.parse_args()

    # Construct the full file path
    # this from the node of itself
    filepath = os.path.join('topology', 'nt_nodes11_RM.json')
    bnsfobj = BNSF(filepath, args.num_clusters)


    total_nodes = bnsfobj.get_total_nodes()
    print(f"Total number of nodes: {total_nodes}")

    set_of_nodes = bnsfobj.get_set_of_nodes()
    print(f"Set of nodes: {set_of_nodes}")

    clusters = bnsfobj.get_clusters()
    print(f"Clusters: {clusters}")




