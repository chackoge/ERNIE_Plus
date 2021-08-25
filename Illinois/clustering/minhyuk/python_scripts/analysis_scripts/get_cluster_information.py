import json

import click
import networkit as nk
import numpy as np
np.set_printoptions(suppress=True, formatter={"float_kind":"{:f}".format})


from python_scripts.utils.utils import file_to_dict,save_histogram
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_num_edges,get_sum_num_degrees,get_intracluster_num_edges,get_intracluster_num_degree,get_intracluster_top_n_indegree_nodes


def evaluate_clustering(cluster_to_id_dict, id_to_cluster_dict, graph, figure_prefix, output_prefix):
    # num clusters
    # histogram cluster sizes
    # min, mean, median, max, 10, 25, 75, 90th percentile
    data_arr = []
    singleton_count = 0
    coverage = 0
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        current_length = len(cluster_member_arr)
        data_arr.append(current_length)
        if(current_length == 1):
           singleton_count += 1
        else:
            coverage += len(cluster_member_arr)


    with open(f"{output_prefix}/clustering.info", "w") as f:
        f.write(f"{coverage} nodes are in non-singleton clusters\n")
        f.write(f"There are {len(cluster_to_id_dict)} number of clusters\n")
        f.write(f"Of these, {singleton_count} are singletons\n")
        f.write(f"min cluster size: {np.min(data_arr)}\n")
        f.write(f"max cluster size: {np.max(data_arr)}\n")
        f.write(f"mean cluster size: {np.mean(data_arr)}\n")
        f.write(f"median cluster size: {np.median(data_arr)}\n")
        f.write(f"10th percentile cluster size: {np.percentile(data_arr, 10)}\n")
        f.write(f"25th percentile cluster size: {np.percentile(data_arr, 25)}\n")
        f.write(f"75th percentile cluster size: {np.percentile(data_arr, 75)}\n")
        f.write(f"90th percentile cluster size: {np.percentile(data_arr, 90)}\n")
        f.write(f"91th percentile cluster size: {np.percentile(data_arr, 91)}\n")
        f.write(f"92th percentile cluster size: {np.percentile(data_arr, 92)}\n")
        f.write(f"93th percentile cluster size: {np.percentile(data_arr, 93)}\n")
        f.write(f"94th percentile cluster size: {np.percentile(data_arr, 94)}\n")
        f.write(f"95th percentile cluster size: {np.percentile(data_arr, 95)}\n")
        f.write(f"96th percentile cluster size: {np.percentile(data_arr, 96)}\n")
        f.write(f"97th percentile cluster size: {np.percentile(data_arr, 97)}\n")
        f.write(f"98th percentile cluster size: {np.percentile(data_arr, 98)}\n")
        f.write(f"99th percentile cluster size: {np.percentile(data_arr, 99)}\n")
        f.write(f"99.9th percentile cluster size: {np.percentile(data_arr, 99.9)}\n")
        f.write(f"99.99th percentile cluster size: {np.percentile(data_arr, 99.99)}\n")
        f.write(f"99.999th percentile cluster size: {np.percentile(data_arr, 99.999)}\n")
        f.write(f"99.9999th percentile cluster size: {np.percentile(data_arr, 99.9999)}\n")
    # save_histogram(20, np.max(data_arr) + 1, 1, data_arr, "Count", "Cluster Sizes", "Cluster Sizes Histogram (>20)", f"{figure_prefix}/cluster_sizes_histogram")


def track_nodes(nodes_of_interest, cluster_to_id_dict, id_to_cluster_dict, output_prefix):
   with open(f"{output_prefix}/nodes_of_interest.info", "w") as f:
       f.write(f"node,cluster_id,cluster_size\n")
       for node_id in nodes_of_interest:
           # print(f"current node is {node_id}")
           if(str(node_id) in id_to_cluster_dict):
               current_cluster_id = id_to_cluster_dict[str(node_id)][0] # assuming that the clusters are non overlapping
               # print(f"node belongs in {current_cluster_id}")
               current_cluster_size = len(cluster_to_id_dict[int(current_cluster_id)])
               # print(f"{current_cluster_id} has {len(cluster_to_id_dict[int(current_cluster_id)])} elements in it")
               f.write(f"{node_id},{id_to_cluster_dict[str(node_id)][0]},{current_cluster_size}\n")

def evaluate_individual_clusters(cursor, table_name, cluster_to_id_dict, id_to_cluster_dict, graph, output_prefix):
    # distribution of modularity scores
    # distribution of conductance
    min_k_arr = []
    modularity_arr = []
    conductance_arr = []
    # the approach that uses sql is below
    use_sql = False
    use_partitioning = False
    if(use_sql):
        with open(f"{output_prefix}/top_nodes_per_cluster.data", "w") as f:
            for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
                if(len(cluster_member_arr) > 20):
                    L = get_num_edges(cursor, table_name)
                    l_s = get_intracluster_num_edges(cursor, table_name, cluster_member_arr)
                    d_s = get_sum_num_degrees(cursor, table_name, cluster_member_arr)
                    equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
                    print(f"{cluster_id} has modularity {equation_2}")
                    modularity_arr.append(equation_2)
                    '''
                    intracluster_node_degree_arr = get_intracluster_num_degree(cursor, table_name, cluster_member_arr)
                    if(len(intracluster_node_degree_arr) > 1):
                        min_k_arr.append(np.min(intracluster_node_degree_arr))
                    N = 5
                    intracluster_top_n_indegree_arr = get_intracluster_top_n_indegree_nodes(cursor, table_name, N, cluster_member_arr)
                    '''
    elif(use_partitioning):
        partition_file = f"{output_prefix}/partition.file"
        with open(partition_file, "w") as fw:
            for i in range(len(id_to_cluster_dict)):
                fw.write(f"{id_to_cluster_dict[str(i)][0]}\n")
        partition = nk.community.readCommunities(partition_file)
        print(f"modularity: {nk.community.Modularity().getQuality(partition, graph)}")
        for subset_id in partition.getSubsetIds():
            conductance = nk.scd.SetConductance(graph, partition.getMembers(subset_id)).run().getConductance()
            print(f"conductance: {conductance}")
        return
    else:
        boundary = 0
        volume = 0

        L = graph.numberOfEdges()
        for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
            if(len(cluster_member_arr) > 1):
                if(len(modularity_arr) % 1000 == 0):
                    print(f"currently done processing {len(modularity_arr)} clusters")
                    print(f"{len(cluster_to_id_dict) - len(modularity_arr)} more clusters to go")
                int_cluster_member_arr = [int(node_id) for node_id in cluster_member_arr]
                l_s = 0
                d_s = 0
                for node in int_cluster_member_arr:
                    d_s += graph.degree(node)

                for cluster_member in int_cluster_member_arr:
                    for neighbor in graph.iterNeighbors(cluster_member):
                        if(neighbor not in int_cluster_member_arr):
                            boundary += 1
                        else:
                            l_s += 1
                    volume += graph.degree(cluster_member)
                l_s /= 2

                equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
                conductance = boundary / (min(volume, 2 * L - volume))
                modularity_arr.append(equation_2)
                conductance_arr.append(conductance)

    '''kinfo is depracated for now due to being too slow
    with open(f"{output_prefix}/k_arr.info", "w") as f:
        f.write(f"// this file contains the distribution information about minimum k in each cluster\n")
        f.write(f"min: {np.min(min_k_arr)}\n")
        f.write(f"max: {np.max(min_k_arr)}\n")
        f.write(f"mean: {np.mean(min_k_arr)}\n")
        f.write(f"median: {np.median(min_k_arr)}\n")
        f.write(f"10th percentile: {np.percentile(min_k_arr, 10)}\n")
        f.write(f"25th percentile: {np.percentile(min_k_arr, 25)}\n")
        f.write(f"75th percentile: {np.percentile(min_k_arr, 25)}\n")
        f.write(f"90th percentile: {np.percentile(min_k_arr, 25)}\n")
    '''

    with open(f"{output_prefix}/modularity.info", "w") as f:
        f.write(f"// this file contains the distribution information about modularity in each cluster\n")
        f.write(f"min modularity:  {np.min(modularity_arr)}\n")
        f.write(f"max modularity:  {np.max(modularity_arr)}\n")
        f.write(f"mean modularity:  {np.mean(modularity_arr)}\n")
        f.write(f"median modularity:  {np.median(modularity_arr)}\n")
        f.write(f"10th percentile modularity:  {np.percentile(modularity_arr, 10)}\n")
        f.write(f"25th percentile modularity:  {np.percentile(modularity_arr, 25)}\n")
        f.write(f"75th percentile modularity:  {np.percentile(modularity_arr, 25)}\n")
        f.write(f"90th percentile modularity:  {np.percentile(modularity_arr, 25)}\n")
        f.write(f"91th percentile modularity: {np.percentile(modularity_arr, 91)}\n")
        f.write(f"92th percentile modularity: {np.percentile(modularity_arr, 92)}\n")
        f.write(f"93th percentile modularity: {np.percentile(modularity_arr, 93)}\n")
        f.write(f"94th percentile modularity: {np.percentile(modularity_arr, 94)}\n")
        f.write(f"95th percentile modularity: {np.percentile(modularity_arr, 95)}\n")
        f.write(f"96th percentile modularity: {np.percentile(modularity_arr, 96)}\n")
        f.write(f"97th percentile modularity: {np.percentile(modularity_arr, 97)}\n")
        f.write(f"98th percentile modularity: {np.percentile(modularity_arr, 98)}\n")
        f.write(f"99th percentile modularity: {np.percentile(modularity_arr, 99)}\n")
        f.write(f"99.9th percentile modularity: {np.percentile(modularity_arr, 99.9)}\n")
        f.write(f"99.99th percentile modularity: {np.percentile(modularity_arr, 99.99)}\n")
        f.write(f"99.999th percentile modularity: {np.percentile(modularity_arr, 99.999)}\n")
        f.write(f"99.9999th percentile modularity: {np.percentile(modularity_arr, 99.9999)}\n")

    with open(f"{output_prefix}/conductance.info", "w") as f:
        f.write(f"// this file contains the distribution information about conductance in each cluster\n")
        f.write(f"min conductance:  {np.min(conductance_arr)}\n")
        f.write(f"max conductance:  {np.max(conductance_arr)}\n")
        f.write(f"mean conductance:  {np.mean(conductance_arr)}\n")
        f.write(f"median conductance:  {np.median(conductance_arr)}\n")
        f.write(f"10th percentile conductance:  {np.percentile(conductance_arr, 10)}\n")
        f.write(f"25th percentile conductance:  {np.percentile(conductance_arr, 25)}\n")
        f.write(f"75th percentile conductance:  {np.percentile(conductance_arr, 25)}\n")
        f.write(f"90th percentile conductance:  {np.percentile(conductance_arr, 25)}\n")
        f.write(f"91th percentile conductance: {np.percentile(conductance_arr, 91)}\n")
        f.write(f"92th percentile conductance: {np.percentile(conductance_arr, 92)}\n")
        f.write(f"93th percentile conductance: {np.percentile(conductance_arr, 93)}\n")
        f.write(f"94th percentile conductance: {np.percentile(conductance_arr, 94)}\n")
        f.write(f"95th percentile conductance: {np.percentile(conductance_arr, 95)}\n")
        f.write(f"96th percentile conductance: {np.percentile(conductance_arr, 96)}\n")
        f.write(f"97th percentile conductance: {np.percentile(conductance_arr, 97)}\n")
        f.write(f"98th percentile conductance: {np.percentile(conductance_arr, 98)}\n")
        f.write(f"99th percentile conductance: {np.percentile(conductance_arr, 99)}\n")
        f.write(f"99.9th percentile conductance: {np.percentile(conductance_arr, 99.9)}\n")
        f.write(f"99.99th percentile conductance: {np.percentile(conductance_arr, 99.99)}\n")
        f.write(f"99.999th percentile conductance: {np.percentile(conductance_arr, 99.999)}\n")
        f.write(f"99.9999th percentile conductance: {np.percentile(conductance_arr, 99.9999)}\n")


@click.command()
@click.option("--input-clusters", required=True, type=click.Path(exists=True), help="Clustering output")
@click.option("--input-network", required=True, type=click.Path(exists=True), help="Input network")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the postgres connection details")
@click.option("--nodes-file", required=True, type=click.Path(exists=True), help="Nodes file")
@click.option("--output-prefix", required=False, type=click.Path(), help="Output file prefix")
@click.option("--figure-prefix", required=False, type=click.Path(), help="Figure file prefix")
def get_cluster_information(input_clusters, input_network, config_file, nodes_file, figure_prefix, output_prefix):
    '''This is the main function that takes in an input clustering output in the format
    where each line is "<cluster number>SPACE<node id>". Input network should be an edge list
    with node ids corresponding to the input network where all the node ids are integers.
    The input nodes file should be a node id for each line in the file.
    The code outputs the following statistics.
    1.  Core coverage
    2.  Number of non-singleton clusters
    3.  Number of nodes in non-singleton clusters
    4.  Modularity distribution
    5.  Total modularity score
    6.  Size distribution
    7.  Intra-cluster conductance distribution (per cluster)
    8.  Tracking high degree nodes and marker nodes
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    graph = nk.readGraph(input_network, nk.Format.EdgeListTabZero)
    cluster_dicts = file_to_dict(input_clusters)
    cluster_to_id_dict = cluster_dicts["cluster_to_id_dict"]
    id_to_cluster_dict = cluster_dicts["id_to_cluster_dict"]
    nodes_of_interest = set()
    with open(nodes_file, "r") as f:
        for line in f:
            nodes_of_interest.add(int(line.strip()))

    evaluate_clustering(cluster_to_id_dict, id_to_cluster_dict, graph, figure_prefix, output_prefix)
    evaluate_individual_clusters(cursor, table_name, cluster_to_id_dict, id_to_cluster_dict, graph, output_prefix)
    track_nodes(nodes_of_interest, cluster_to_id_dict, id_to_cluster_dict, output_prefix)


if __name__ == "__main__":
    get_cluster_information()
