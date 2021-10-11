import datetime
from timeit import default_timer

import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict,run_graclus,write_new_sorted_cluster_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict


def get_validity_and_min_k(cursor, table_name, graph, cluster_to_id_dict, inverse_node_map):
    '''This function will test whether the clusters in the input clustering are valid.
    If at least one cluster is valid, then it will output True for is_valid
    and return the cluster_ids that are invalid. It does not modify the input clustering.
    '''
    return {
        "is_valid": True,
        "num_subclusters": len(cluster_to_id_dict),
    }

def get_best_graclus(cursor, table_name, graph, compacted_graph_filename, graclus_output_prefix, inverse_node_map, local_search):
    '''This function will run graclus and return whether graclus was able to decompose
    the graph into at least one valid cluster. If so, then it will output the updated clustering
    in best_cluster_to_id_dict with the invalid clusters removed.
    '''
    best_cluster_to_id_dict = None
    best_num_subclusters = 0
    num_clusters = 2
    invalid_nodes = []
    cluster_to_id_dict = run_graclus(compacted_graph_filename, num_clusters, local_search, graclus_output_prefix)
    validity_and_min_k = get_validity_and_min_k(cursor, table_name, graph, cluster_to_id_dict, inverse_node_map)
    if(validity_and_min_k["is_valid"]):
        best_cluster_to_id_dict = cluster_to_id_dict
        best_num_subclusters = validity_and_min_k["num_subclusters"]

    if(not best_num_subclusters <= num_clusters):
        raise Exception(f"{best_num_subclusters} subclusters found which is more than {num_clusters}")
    return {
        "best_cluster_to_id_dict": best_cluster_to_id_dict,
        "num_clusters": best_num_subclusters,
    }


def run_graclus_on_cluster(cursor, table_name, graph, cluster_to_id_dict, cluster_id_to_split, output_prefix, local_search):
    ''' This runs graclus on a cluster specified by the cluster_id_to_split
    and updates the cluster_to_id_dict by creating new clusters with cluster id
    starting from the current max cluster_id  + 1.
    Note that it does erase the original cluster
    '''
    # the code below simply creates a subgraph with a renumbered mapping of nodes for graclus
    # and writes that subgraph in METIS format for graclus to use
    new_cluster_ids = None
    subgraph = nk.graphtools.subgraphFromNodes(graph, [int(integer_node_id) for integer_node_id in cluster_to_id_dict[cluster_id_to_split]])
    new_node_map = nk.graphtools.getContinuousNodeIds(subgraph)
    compacted_graph = nk.graphtools.getCompactedGraph(subgraph, new_node_map)
    compacted_graph_filename = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}.tsv"
    graclus_output_prefix = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}"
    inverse_node_map = {new_id: old_id for old_id,new_id in new_node_map.items()}
    nk.writeGraph(compacted_graph, compacted_graph_filename, nk.Format.METIS)

    # this code gets the best graclus which means it's either none if graclus failed to give
    # any valid cluster or a dictionary containing information about the valid clusters if graclus succeeded
    best_graclus_result = get_best_graclus(cursor, table_name, graph, compacted_graph_filename, graclus_output_prefix, inverse_node_map, local_search)
    compacted_graph_clusters = best_graclus_result["best_cluster_to_id_dict"]
    num_clusters = best_graclus_result["num_clusters"]
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
    }


@click.command()
@click.option("--config-file", required=False, type=click.Path(exists=True), help="The config file containing the postgres connection details")
@click.option("--network", required=True, type=click.Path(exists=True), help="Integer labelled edgelist")
@click.option("--clustering", required=False, type=click.Path(exists=True), help="Initial clustering to begin with as an alternative to graclus")
@click.option("--local-search", required=False, type=int, default=0, help="The local search parameter for graclus")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def single_graclus(config_file, network, clustering, local_search, output_prefix):
    '''This is the main function that will take in a tsv integer labelled network and recursively
    run graclus on the network and its clusters until we can no longer split a cluster into at least
    one valid constituent where validity is defined by having a positive modularity score
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
    initial_k_num_cluters_tuple_arr = None

    if(clustering is None):
        # if an initial clustering is not provided, then we simply start by running graclus on the initial network
        initial_graclus_filename = f"{output_prefix}/initial_graph"
        inverse_node_map = None
        best_graclus_result = get_best_graclus(cursor, table_name, graph, network, initial_graclus_filename, inverse_node_map)
        cluster_to_id_dict = best_graclus_result["best_cluster_to_id_dict"]
        initial_graclus_num_clusters = best_graclus_result["num_clusters"]
    else:
        # if an initial clustering is provided, then we start with the initial clustering directly
        cluster_to_id_dict = file_to_dict(clustering)["cluster_to_id_dict"]

    # this stack stores the list of clusters to be split
    cluster_id_stack = list(filter(lambda cluster_id: len(cluster_to_id_dict[cluster_id]) > 1, cluster_to_id_dict.keys()))

    with open(f"{output_prefix}/single_graclus.log", "w") as f:
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
            f.write(f"// The best initial graclus produced {len(cluster_to_id_dict)} clusters\n")

    iteration_number = 0 # this is purely for logging purposes
    with open(f"{output_prefix}/single_graclus.log", "a") as f:
        start_time = default_timer()
        while(len(cluster_id_stack) > 0):
            f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] Iteration {iteration_number} - {len(cluster_id_stack)} in the stack\n")
            iteration_number += 1
            # current_cluster_id is the cluster_id we wil attempt to split using graclus in this iteration
            current_cluster_id = int(cluster_id_stack.pop())
            cluster_member_arr = cluster_to_id_dict[current_cluster_id]
            f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] current cluster size is {len(cluster_member_arr)}\n")
            f.flush()
            decomposed_into = []
            if(len(cluster_member_arr) > 1):
                # this should always be the case. If we don't enter this if statement,
                # an assert error will be raised. The cluster stack should always have non-singleton clusters to be split
                graclus_cluster_result = run_graclus_on_cluster(cursor, table_name, graph, cluster_to_id_dict, current_cluster_id, output_prefix, local_search)
                new_cluster_ids = graclus_cluster_result["new_cluster_ids"]
                num_clusters = graclus_cluster_result["num_clusters"]

                # new_cluster_ids is an array of cluster_ids as a result of running graclus on the subgraph
                # if graclus successfully decomposed the current cluster into valid clusters, it will have either
                # 1 or 2 new cluster ids
                if(new_cluster_ids is None):
                    raise Exception("RecursiveGraclus returned None as result which is not possible when not rejecting any subclusters.")
                elif(len(new_cluster_ids) > 0):
                    # the current cluster has successfully decomposed into at least one valid cluster
                    f.write(f"[{datetime.timedelta(seconds=default_timer() - start_time)}] {current_cluster_id} decomposed into {num_clusters} clusters\n")
                else:
                    raise Exception("New cluster ids was not none but contained nothing in it")
            else:
                # this should never happen if graclus is run with k and m constraints
                raise Exception("Cluster member stack should only contain valid clusters")
            f.flush()

    if(cluster_to_id_dict):
        # we can now write the updated clustering and the singleton nodes (unassigned_nodes) to a clustering file where the format is "cluster_id<SPACE>node_id"
        # this clustering will also be sorted by size where cluster_id of 0 is the cluster with the most nodes
        write_new_sorted_cluster_dict(cluster_to_id_dict, [], f"{output_prefix}/single_graclus")


if __name__ == "__main__":
    single_graclus()
