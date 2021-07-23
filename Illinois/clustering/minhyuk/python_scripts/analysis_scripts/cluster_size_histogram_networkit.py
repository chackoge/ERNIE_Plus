import json

import click
import matplotlib.pyplot as plt
import networkit as nk
import numpy as np

from python_scripts.utils.utils import mapping_to_dict,save_histogram

@click.command()
@click.option("--input-clusters", required=True, type=click.Path(exists=True), help="Clustering output")
@click.option("--input-network", required=True, type=click.Path(exists=True), help="Input network")
@click.option("--minimum-size", required=False, type=int, default=6, help="Minimum cluster size to report in histogram")
@click.option("--high-degree-nodes", required=False, type=click.Path(), help="High in-degree nodes to analyze")
@click.option("--mapping-file", required=False, type=click.Path(), help="Mapping from integer labels to dimensions ids")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Output histogram prefix")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def cluster_size_histogram_networkit(input_clusters, input_network, minimum_size, high_degree_nodes, mapping_file, figure_prefix, output_prefix):
    '''This is the main function that takes in an input clustering output in the format
    where line i has "<cluster number>" for node i. Input network should be an edge list
    with node ids corresponding to the input network where all the node ids are integers
    '''
    graph = nk.readGraph(input_network, nk.Format.EdgeListTabZero)
    partition = nk.community.readCommunities(input_clusters)
    sizes = partition.subsetSizes()
    pruned_sizes = []
    for size in sizes:
        if(size > minimum_size - 1):
            pruned_sizes.append(size)
    # sizes.sort(reverse=True)
    # ax = plt.subplot(1, 1, 1)
    # ax.set_ylabel("size")
    # ax.plot(pruned_sizes)
    # ax.ticklabel_format(style="plain")
    # plt.savefig(f"{figure_prefix}/cluster_number_to_size_at_least_{minimum_size}_plot.png")
    save_histogram(6, max(pruned_sizes) + 1, 1, pruned_sizes, "Count", "Cluster Sizes", f"{figure_prefix}", f"{figure_prefix}/cluster_number_to_size_at_least_{minimum_size}_plot")
    # this will print a tabluar format like
    '''
    -------------------  -------------
    # communities          number
    min community size     number
    max community size     number
    avg. community size    number
    modularity             number
    -------------------  -------------
    '''
    nk.community.inspectCommunities(partition, graph)

    high_indegree_nodes = {} # here we store the integer ids of all the high indegree nodes
    dimensions_id_to_integer_dict = {}
    if(high_degree_nodes is not None):
        if(mapping_file is None):
            print("mapping file must be provided is high indegree nodes is provided")
            exit(1)
        dimensions_id_to_integer_dict = mapping_to_dict(mapping_file)["id_to_integer_dict"]
        with open(high_degree_nodes, "r") as f:
            for line in f:
                dimensions_id,indegree= line.split()
                high_indegree_nodes[dimensions_id_to_integer_dict[dimensions_id]] = indegree

        cluster_degree_dict = {}
        with open(output_prefix + f"_cluster.data", "w") as f:
            for cluster_index in partition.getVector():
                current_members = partition.getMembers(cluster_index)
                current_subgraph = nk.graphtools.subgraphFromNodes(graph, current_members)
                f.write("---\n")
                f.write(f"cluster number: {cluster_index}\n")
                f.write(f"There are {current_subgraph.numberOfNodes()} nodes in cluster {cluster_index}\n")
                # making sure the subgraph was constructed properly by checking the number of nodes
                assert current_subgraph.numberOfNodes() == len(current_members)
                if(len(partition.getMembers(cluster_index)) > 5):
                    # this is a relevant component we want to analyze for how many high indegree nodes there are
                    high_indegree_node_count = 0
                    for member in current_subgraph.iterNodes():
                        if(int(member) in high_indegree_nodes):
                            high_indegree_node_count += 1
                    f.write(f"There are {high_indegree_node_count} high in-degree nodes in cluster {cluster_index}\n")
                    f.write(f"The average degree within cluster {cluster_index} is {current_subgraph.numberOfEdges() * 2 / current_subgraph.numberOfNodes()}\n")
                    if(int(high_indegree_node_count) not in cluster_degree_dict):
                        cluster_degree_dict[int(high_indegree_node_count)] = 0
                    cluster_degree_dict[int(high_indegree_node_count)] += 1
        with open(output_prefix + f"_cluster_summary.data", "w") as f:
            for cluster_high_indegree_node_count in max(cluster_degree_dict.keys()):
                f.write(f"{cluster_degree_dict[cluster_high_indegree_node_count]} clusters with {cluster_high_degre_node_count} high in-degree nodes\n")



if __name__ == "__main__":
    cluster_size_histogram_networkit()
