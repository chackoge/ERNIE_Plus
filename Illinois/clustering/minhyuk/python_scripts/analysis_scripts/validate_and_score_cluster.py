import json

import click
import networkit as nk
import numpy as np

from python_scripts.utils.utils import file_to_dict


def validate_clustering(k, b, core_nodes, cluster_to_id_dict, id_to_cluster_dict, graph):
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        integer_cluster_member_arr = [int(node) for node in cluster_member_arr]
        subgraph = nk.graphtools.subgraphFromNodes(graph, integer_cluster_member_arr)
        cc = nk.components.ConnectedComponents(subgraph)
        cc.run()
        # This checks for the first property
        if(cc.numberOfComponents() != 1):
            # this cluster is not connected
            print(f"Cluster {cluster_id} has {cc.numberOfComponents()} components")
            return False

        # This checks for the second property
        subgraph_core_nodes = set(core_nodes).intersection(set(integer_cluster_member_arr))
        for subgraph_core_node in subgraph_core_nodes:
            if(subgraph.degree(subgraph_core_node) < k):
                # this core node has degree less than k
                print(f"Node {subgraph_core_node} has degree {subgraph.degree(subgraph_core_node)} which is less than the minimum required degree {k}")
                return False

        # This checks for the third property
        if(len(subgraph_core_nodes) > b):
            # this cluster has too many core nodes
            print(f"Cluster {cluster_id} has {len(subgraph_core_nodes)} core nodes which is more than tha maximum allowed amount {b}")
            return False

        # This checks for the fourth property
        for subgraph_core_node in subgraph_core_nodes:
            is_adjacent = False
            for subgraph_core_node_neighbor in subgraph.iterNeighbors(subgraph_core_node):
                if(subgraph_core_node_neighbor in subgraph_core_nodes):
                    is_adjacent = True
                    break
            if(not is_adjacent):
                # This core node is not adjacent to a core node
                print(f"Core node {subgraph_core_node} is not adjacent to any core nodes")
                return False
    return True


def score_clustering(core_nodes, cluster_to_id_dict, id_to_cluster_dict, graph):
    coverage = len(core_nodes)
    connectivity = 0
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        integer_cluster_member_arr = [int(node) for node in cluster_member_arr]
        subgraph = nk.graphtools.subgraphFromNodes(graph, integer_cluster_member_arr)
        subgraph_core_nodes = set(core_nodes).intersection(set(integer_cluster_member_arr))
        for subgraph_node in integer_cluster_member_arr:
            if(subgraph_node not in subgraph_core_nodes):
                subgraph_neighbors_of_non_core_node= list(subgraph.iterNeighbors(subgraph_node))
                only_core_neighbors = set(subgraph_neighbors_of_non_core_node).intersection(subgraph_core_nodes)
                # connectivity += (len(subgraph_neighbors_of_non_core_node) - len(only_core_neighbors))
                connectivity += len(only_core_neighbors)
    return {
        "coverage": coverage,
        "connectivity": connectivity,
    }


@click.command()
@click.option("--input-clusters", required=True, type=click.Path(exists=True), help="Clustering output")
@click.option("--input-network", required=True, type=click.Path(exists=True), help="Input network")
@click.option("--core-nodes-file", required=True, type=click.Path(exists=True), help="Core nodes file")
@click.option("--k", required=True, type=int, help="The minimum connectivity among core members")
@click.option("--b", required=True, type=int, help="The maximum number of core members in any cluster")
@click.option("--output-prefix", required=False, type=click.Path(), help="Output file prefix")
def validate_and_score_cluster(input_clusters, input_network, core_nodes_file, k, b, output_prefix):
    '''This is the main function that takes in an input clustering output in the format
    where each line is "<cluster number>SPACE<node id>". Input network should be an edge list
    with node ids corresponding to the input network where all the node ids are integers.
    The input core nodes file should be a node id for each line in the file. The output
    is a score of the clustering based on these criteria in order of precedence
        1. Core-covearge: the total number of core nodes
        2. Non-core-to-core-connectivity: the total number of edges between core and non-core
           nodes
    However, all input clusterings must satisfy four properties
        1. Each cluster is a connected subgraph of the network
        2. The core members of each cluster have at least degree k among themselves
        3. Each cluster has at most b core members
        4. Every non-core node is adjacent to at least one core node
    '''
    graph = nk.readGraph(input_network, nk.Format.EdgeListTabZero)
    cluster_dicts = file_to_dict(input_clusters)
    cluster_to_id_dict = cluster_dicts["cluster_to_id_dict"]
    id_to_cluster_dict = cluster_dicts["id_to_cluster_dict"]
    core_nodes = set()
    with open(core_nodes_file, "r") as f:
        for line in f:
            core_nodes.add(int(line.strip()))
    is_valid = validate_clustering(k, b, core_nodes, cluster_to_id_dict, id_to_cluster_dict, graph)
    if(is_valid):
        print(score_clustering(core_nodes, cluster_to_id_dict, id_to_cluster_dict, graph))


if __name__ == "__main__":
    validate_and_score_cluster()
