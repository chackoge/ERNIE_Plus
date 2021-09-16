import datetime
from timeit import default_timer

import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict,run_mcl,run_graclus,write_new_sorted_cluster_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_num_edges,get_sum_num_degrees,get_intracluster_num_edges,get_intracluster_num_degree






def get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, inverse_node_map, k, m):
    ''' equation 2 is defined by \frac{l_{s}}{L} - (\frac{d_{s}}{2L})^{2} > m where m is zero
    where l_s is the number of edges in cluster s, L is the number of edges in the
    entire network, and d_s is the total sum of the degrees of each node inside cluster s
    When this value is greater than t, it is considered a valid module in terms of modularity
    criterion. [deprecated option size b] Each cluster must also be of size at least B.
    '''
    if(k > 0 and m > float("-inf") and len(cluster_member_arr) == 1):
        # singletons are never valid clusters
        return {
            "is_valid": False,
        }

    node_degree_valid = True
    equation_2 = None
    intracluster_node_degree_arr = []

    use_sql = False
    if(use_sql):
        intracluster_node_degree_tuple_arr = get_intracluster_num_degree(cursor, table_name, cluster_member_arr)
        intracluster_node_degree_arr = [int(tup[1]) for tup in intracluster_node_degree_tuple_arr],
        for node,degree in intracluster_node_degree_arr:
            if(degree < k):
                node_degree_valid = False

        L = get_num_edges(cursor, table_name)
        l_s = get_intracluster_num_edges(cursor, table_name, cluster_member_arr)
        d_s = get_sum_num_degrees(cursor, table_name, cluster_member_arr)
        equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
    elif(len(cluster_member_arr) < 500):
        L = graph.numberOfEdges()
        int_cluster_member_arr = None
        if(inverse_node_map):
            int_cluster_member_arr = [inverse_node_map[int(node_id)] for node_id in cluster_member_arr]
        else:
            int_cluster_member_arr = [int(node_id) for node_id in cluster_member_arr]
        l_s = 0
        d_s = 0
        for node in int_cluster_member_arr:
            d_s += graph.degree(node)
        for cluster_member in int_cluster_member_arr:
            current_k = 0
            for neighbor in graph.iterNeighbors(cluster_member):
                if(neighbor in int_cluster_member_arr):
                    l_s += 1
                    current_k += 1
            if(current_k < k):
                node_degree_valid = False
            intracluster_node_degree_arr.append(current_k)
        l_s /= 2
        equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
    else:
        int_cluster_member_arr = None
        if(inverse_node_map):
            int_cluster_member_arr = [inverse_node_map[int(node_id)] for node_id in cluster_member_arr]
        else:
            int_cluster_member_arr = [int(node_id) for node_id in cluster_member_arr]
        subgraph = nk.graphtools.subgraphFromNodes(graph, int_cluster_member_arr)
        L = graph.numberOfEdges()
        l_s = subgraph.numberOfEdges()
        d_s = 0
        for node in int_cluster_member_arr:
            d_s += graph.degree(node)
            current_k = subgraph.degree(node)
            intracluster_node_degree_arr.append(current_k)
            if(current_k < k):
                node_degree_valid = False
        equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
    return {
       "is_valid": equation_2 >= m and node_degree_valid,
       "equation_2": equation_2,
       "k_arr": intracluster_node_degree_arr,
    }


def get_validity_and_min_k(cursor, table_name, graph, cluster_to_id_dict, inverse_node_map, k, m):
    ''' Do not call this function if all you have are singletons
    '''
    min_k = None
    singleton_cluster = False
    invalid_cluster_id_arr = []
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        cluster_info_dict = None
        if(len(cluster_member_arr) > 1):
            cluster_info_dict = get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, inverse_node_map, k, m)
            clustering_validity = cluster_info_dict["is_valid"]
            if(clustering_validity):
                # the k_arr will be None if it's a singleton which is allowed when recursive graclus
                # is run without any validity checking
                if(len(cluster_info_dict["k_arr"]) > 0):
                    if(min_k is None):
                        min_k = np.min(cluster_info_dict["k_arr"])
                    else:
                        min_k = min(min_k, np.min(cluster_info_dict["k_arr"]))
            elif(k == 0 and m == float("-inf") and not clustering_validity):
                raise Exception("When k is 0 and m is float('-inf'), every cluster should be valid")
            else:
                invalid_cluster_id_arr.append(cluster_id)
        else:
            singleton_cluster = True
    return {
        "is_valid": not singleton_cluster and len(invalid_cluster_id_arr) == 0,
        "invalid_cluster_id_arr": invalid_cluster_id_arr,
        "min_k": min_k,
        "num_subclusters": len(cluster_to_id_dict) - len(invalid_cluster_id_arr),
    }

def get_best_graclus(cursor, table_name, graph, compacted_graph_filename, graclus_output_prefix, inverse_node_map, k, m):
    best_cluster_to_id_dict = None
    best_k = 0
    best_num_subclusters = 0
    num_clusters = 2
    cluster_to_id_dict = run_graclus(compacted_graph_filename, num_clusters, graclus_output_prefix)
    validity_and_min_k = get_validity_and_min_k(cursor, table_name, graph, cluster_to_id_dict, inverse_node_map, k, m)
    if(validity_and_min_k["is_valid"]):
        best_cluster_to_id_dict = cluster_to_id_dict
        for invalid_cluster_id in validity_and_min_k["invalid_cluster_id_arr"]:
            best_cluster_to_id_dict.pop(invalid_cluster_id)
        best_k = validity_and_min_k["min_k"]
        best_num_subclusters = validity_and_min_k["num_subclusters"]
    return {
        "best_cluster_to_id_dict": best_cluster_to_id_dict,
        "num_clusters": best_num_subclusters,
        "min_k": best_k,
        "num_invalid_cluster_ids": len(validity_and_min_k["invalid_cluster_id_arr"]),
    }


def run_graclus_on_cluster(cursor, table_name, graph, cluster_to_id_dict, cluster_id_to_split, output_prefix, k, m):
    ''' This runs graclus on a cluster specified by the cluster_id_to_split
    and updates the cluster_to_id_dict by creating new clusters with cluster id
    starting from the current max cluster_id  + 1.
    Note that it does erase the original cluster
    '''
    new_cluster_ids = None
    subgraph = nk.graphtools.subgraphFromNodes(graph, [int(integer_node_id) for integer_node_id in cluster_to_id_dict[cluster_id_to_split]])
    new_node_map = nk.graphtools.getContinuousNodeIds(subgraph)
    compacted_graph = nk.graphtools.getCompactedGraph(subgraph, new_node_map)
    compacted_graph_filename = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}.tsv"
    graclus_output_prefix = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}"
    inverse_node_map = {new_id: old_id for old_id,new_id in new_node_map.items()}
    nk.writeGraph(compacted_graph, compacted_graph_filename, nk.Format.METIS)
    best_graclus_result = get_best_graclus(cursor, table_name, graph, compacted_graph_filename, graclus_output_prefix, inverse_node_map, k, m)
    compacted_graph_clusters = best_graclus_result["best_cluster_to_id_dict"]
    num_clusters = best_graclus_result["num_clusters"]
    min_k = best_graclus_result["min_k"]
    num_invalid_cluster_ids = best_graclus_result["num_invalid_cluster_ids"]
    if(compacted_graph_clusters is not None):
        new_cluster_ids = []
        new_cluster_index = max(cluster_to_id_dict.keys()) + 1
        for cluster,cluster_members in compacted_graph_clusters.items():
            cluster_to_id_dict[new_cluster_index] = []
            for new_cluster_member_id in cluster_members:
                cluster_to_id_dict[new_cluster_index].append(str(inverse_node_map[int(new_cluster_member_id)]))
            new_cluster_ids.append(new_cluster_index)
            new_cluster_index += 1
        cluster_to_id_dict[cluster_id_to_split] = []
    return {
        "new_cluster_ids": new_cluster_ids,
        "num_clusters": num_clusters,
        "min_k": min_k,
        "num_invalid_cluster_ids": num_invalid_cluster_ids,
    }


@click.command()
@click.option("--config-file", required=False, type=click.Path(exists=True), help="The config file containing the postgres connection details")
@click.option("--network", required=True, type=click.Path(exists=True), help="Integer labelled edgelist")
@click.option("--clustering", required=False, type=click.Path(exists=True), help="Initial clustering to begin with as an alternative to graclus")
@click.option("--k", required=False, type=int, default=0, help="The minimum connectivity among each other in a cluster to be considered valid")
@click.option("--m", required=False, type=float, default=float("-inf"), help="The minimum modularity threshold for each cluster")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def recursive_graclus(config_file, network, clustering, k, m, output_prefix):
    '''This is the main function that will take in a tsv integer labelled network and recursively
    run graclus on the network and its clusters until we can no longer split a cluster into its
    valid constituents where valid is defined by a positive modularity score
    '''
    cursor = None
    connection = None
    table_name = None
    if(config_file is not None):
        cursor_client_dict = get_cursor_client_dict(config_file)
        cursor = cursor_client_dict.pop("cursor", none)
        connection = cursor_client_dict.pop("connection", none)
        table_name = cursor_client_dict.pop("table_name", None)
    graph = nk.readGraph(network, nk.Format.EdgeListTabZero)
    cluster_to_id_dict = None
    initial_graclus_cluster_num = None
    min_k = None
    initial_k_num_cluters_tuple_arr = None
    if(clustering is None):
        initial_graclus_filename = f"{output_prefix}/initial_graph"
        inverse_node_map = None
        best_graclus_result = get_best_graclus(cursor, table_name, graph, network, initial_graclus_filename, inverse_node_map, k, m)
        cluster_to_id_dict = best_graclus_result["best_cluster_to_id_dict"]
        initial_graclus_num_clusters = best_graclus_result["num_clusters"]
        min_k = best_graclus_result["min_k"]
    else:
        cluster_to_id_dict = file_to_dict(clustering)["cluster_to_id_dict"]

    cluster_id_stack = list(filter(lambda cluster_id: len(cluster_to_id_dict[cluster_id]) > 1, cluster_to_id_dict.keys()))

    with open(f"{output_prefix}/recursive_graclus.log", "w") as f:
        if(clustering is None):
            f.write(f"// No clustering was provided so we are running graclus initially\n")
        else:
            f.write(f"// An initial clustering was provided so we are not running graclus initially\n")
        f.write(f"// we start with {len(cluster_id_stack)} clusters\n")
        if(clustering is None and cluster_to_id_dict is None):
            f.write(f"// No way of running graclus could produce a clustering of only valid clusters. Terminating.\n")
        elif(clustering is None and len(cluster_to_id_dict) == 1):
            f.write(f"// The best initial graclus failed to produce more than one cluster. Terminating.\n")
        elif(clustering is None and len(cluster_to_id_dict) > 1):
            f.write(f"// The best initial graclus produced {len(cluster_to_id_dict)} clusters with min k {min_k}\n")
            f.write(f"// -- Information about all the Leiden runs\n")
            for min_k,num_clusters in initial_k_num_clusters_tuple_arr:
                f.write(f"// ---- min k of {min_k} and {num_clusters} clusters \n")


    iteration_number = 0 # this is purely for logging purposes
    with open(f"{output_prefix}/recursive_graclus.log", "a") as f:
        start_time = default_timer()
        while(len(cluster_id_stack) > 0):
            # print(f"A new iteration!")
            f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] Iteration {iteration_number} - {len(cluster_id_stack)} in the stack\n")
            iteration_number += 1
            current_cluster_id = int(cluster_id_stack.pop())
            cluster_member_arr = cluster_to_id_dict[current_cluster_id]
            f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] current cluster size is {len(cluster_member_arr)}\n")
            f.flush()
            # array for logging and tracing purposes
            decomposed_into = []
            # print(f"-- In this iteration, we are inspecting cluster {current_cluster_id} with members {cluster_member_arr}")
            # if(len(cluster_member_arr) > 1):
                # cluster_info_dict = get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, None, k, m)
            if(len(cluster_member_arr) > 1): # and cluster_info_dict["is_valid"]):
                # print(f"-- cluster {current_cluster_id} with members {cluster_member_arr} is a valid cluster")
                graclus_cluster_result = run_graclus_on_cluster(cursor, table_name, graph, cluster_to_id_dict, current_cluster_id, output_prefix, k, m)
                new_cluster_ids = graclus_cluster_result["new_cluster_ids"]
                num_clusters = graclus_cluster_result["num_clusters"]
                min_k = graclus_cluster_result["min_k"]
                num_invalid_cluster_ids = graclus_cluster_result["num_invalid_cluster_ids"]
                # extending instead of pushing every element
                if(new_cluster_ids is None):
                    f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] {current_cluster_id} could not be decomposed. There were {num_invalid_cluster_ids} invalid clusters\n")
                elif(len(new_cluster_ids) == 1):
                    # the current cluster dissolved into itself
                    f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] {current_cluster_id} dissolved into itself\n")
                elif(len(new_cluster_ids) > 1):
                    # the current cluster has successfully decomposed into all valid clusters
                    f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] {current_cluster_id} decomposed into {num_clusters} clusters and min k {min_k}\n")
                    cluster_id_stack.extend(new_cluster_ids)
                else:
                    raise Exception("New cluster ids was not none but contained nothing in it")
            else:
                # this should never happen if recursive graclus is run with k and m constraints
                raise Exception("Cluster member stack should only contain valid clusters")
            f.flush()

    if(cluster_to_id_dict):
        write_new_sorted_cluster_dict(cluster_to_id_dict, [], f"{output_prefix}/recursive_graclus")


if __name__ == "__main__":
    recursive_graclus()
