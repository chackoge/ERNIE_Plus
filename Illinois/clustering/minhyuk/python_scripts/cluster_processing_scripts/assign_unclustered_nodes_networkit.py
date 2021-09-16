from functools import reduce
import json
import multiprocessing
import queue
from heapq import heapify
from heapq import heappush
from heapq import heappop

import click
import matplotlib.pyplot as plt
import numpy as np
import networkit as nk
import psycopg2

from python_scripts.utils.utils import file_to_dict,save_scatter,write_new_sorted_cluster_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_intracluster_query_integer_id_indegree,get_intracluster_query_integer_id_outdegree,get_all_integer_ids,get_all_id_and_inoutdegree_node_table,get_all_id_and_indegree_node_table,get_all_id_and_outdegree_node_table


def find_best_cluster(current_id, graph, id_to_cluster_dict, cluster_to_id_dict, core_nodes, min_degree, cluster_criterion):
    def collect_degrees(u, v, weight, edge_id):
        if(str(v) in id_to_cluster_dict):
            outgoing_cluster_id = id_to_cluster_dict[str(v)][0]
            if(outgoing_cluster_id not in cluster_count_dict):
                cluster_count_dict[outgoing_cluster_id] = 0
            cluster_count_dict[outgoing_cluster_id] += 1

    cluster_count_dict = {}
    if(cluster_criterion == "max_outdegree_to_c"):
        graph.forEdgesOf(int(current_id), collect_degrees)
    elif(cluster_criterion == "max_indegree_to_c"):
        graph.forInEdgesOf(int(current_id), collect_degrees)
    elif(cluster_criterion == "max_totaldegree_to_c"):
        graph.forEdgesOf(int(current_id), collect_degrees)
        graph.forInEdgesOf(int(current_id), collect_degrees)


    best_cluster = max(cluster_count_dict, key=lambda key: cluster_count_dict[key] / len(cluster_to_id_dict[key]))
    best_degree = cluster_count_dict[best_cluster]
    best_proportion = best_degree / len(cluster_to_id_dict[best_cluster])
    if(best_degree < min_degree):
        best_cluster = None
        best_degree = 0
        best_proportion = 0

    return {
        "best_cluster": best_cluster,
        "best_degree": best_degree,
        "best_proportion": best_proportion,
    }


@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help="Clustering output from another method")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing postgres connection information")
@click.option("--network-file", required=True, type=click.Path(exists=True), help="The tsv edgelist of the whole network")
@click.option("--min-degree", required=True, type=int, help="Minimum degree connection to the cluster")
@click.option("--core-nodes-file", required=True, type=click.Path(exists=True), help="The core nodes file containing the core nodes")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--cluster-criterion", required=True, type=click.Choice(["max_outdegree_to_c", "max_indegree_to_c", "max_totaldegree_to_c"]), help="Criterion to select which cluster a given unclustered node should be assigned to")
def assign_unclustered_nodes(clustering, config_file, network_file, min_degree, core_nodes_file, output_prefix, cluster_criterion):
    '''This is the main command that takes in an input clustering and a network to assign unclustered nodes based on the criteria.
    The core nodes file should contain a node id for each line. The clustering file should be in a format "<cluster number>SPACE<node id>"
    The unassigned nodes will be assigned to a new cluster based on their indegree/outdegree/totaldegree to one of the clusters in the
    clustering that will maximize the criterion.
    '''

    cluster_dicts = file_to_dict(clustering)
    cluster_to_id_dict = cluster_dicts["cluster_to_id_dict"]
    id_to_cluster_dict = cluster_dicts["id_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    node_table_name = cursor_client_dict.pop("node_table_name", None)
    edgelist_reader= nk.graphio.EdgeListReader("\t", 0, directed=True)
    graph = edgelist_reader.read(network_file)


    updated_cluster_to_id_dict = cluster_to_id_dict.copy()
    with open(f"{output_prefix}/assign_unclustered_nodes_{cluster_criterion}_{min_degree}.log", "w") as f:
        f.write(f"{len(cluster_to_id_dict)} clusters to be looked through including singleton clusters\n")
    num_unassigned_nodes = 0
    all_ids = [str(node_id) for node_id in get_all_integer_ids(cursor, table_name)]
    unassigned_nodes = []
    with open(f"{output_prefix}/assign_unclustered_nodes_{cluster_criterion}_{min_degree}.log", "a") as f:
        f.write(f"{len(all_ids) - len(id_to_cluster_dict)} nodes without assignment\n")
    # TODO: maybe  filter out nodes with degree lower than min-degree

    node_with_at_least_min_degree = None
    if(cluster_criterion == "max_outdegree_to_c"):
        node_with_at_least_min_degree = set(get_all_id_and_outdegree_node_table(cursor, min_degree, node_table_name))
    elif(cluster_criterion == "max_indegree_to_c"):
        node_with_at_least_min_degree = set(get_all_id_and_indegree_node_table(cursor, min_degree, node_table_name))
    elif(cluster_criterion == "max_totaldegree_to_c"):
        node_with_at_least_min_degree = set(get_all_id_and_inoutdegree_node_table(cursor, min_degree, node_table_name))

    with open(f"{output_prefix}/assign_unclustered_nodes_{cluster_criterion}_{min_degree}.log", "a") as f:
        f.write(f"{len(node_with_at_least_min_degree)} nodes that meet at least the min degree criteria without cluster specificity\n")

    core_nodes = set()
    with open(core_nodes_file, "r") as f:
        for line in f:
            core_nodes.add(int(line.strip()))

    with open(f"{output_prefix}/assign_unclustered_nodes_{cluster_criterion}_{min_degree}.log", "a") as f:
        for current_id in all_ids:
            current_id_cluster = None
            current_id_cluster_length = None
            if(current_id in id_to_cluster_dict):
                current_id_cluster = id_to_cluster_dict[current_id][0]
                current_id_cluster_length = len(cluster_to_id_dict[current_id_cluster])
            if(current_id not in id_to_cluster_dict or current_id_cluster_length == 1):
                num_unassigned_nodes += 1
                # this is an unclustered node since it does not exist in our current clustering
                # we have picked the max cluster
                if(int(current_id) in node_with_at_least_min_degree):
                    best_cluster_dict = find_best_cluster(current_id, graph, id_to_cluster_dict, cluster_to_id_dict, core_nodes, min_degree, cluster_criterion)
                    best_cluster = best_cluster_dict["best_cluster"]
                    best_degree  = best_cluster_dict["best_degree"]
                    best_proportion  = best_cluster_dict["best_proportion"]

                    if(best_proportion > 0):
                        f.write(f"{current_id} went to {best_cluster} where it has {best_proportion} {cluster_criterion}\n")
                        updated_cluster_to_id_dict[best_cluster].append(current_id)
                        if(current_id_cluster is not None):
                            cluster_to_id_dict.pop(current_id_cluster)
                    else:
                        unassigned_nodes.append(current_id)
                        f.write(f"{current_id} did not get assigned to anywhere based on the best proportion for {cluster_criterion} being {best_proportion}\n")
                else:
                    unassigned_nodes.append(current_id)
                    f.write(f"{current_id} did not get assigned to anywhere because its degree is not at least {min_degree}\n")

        f.write(f"{num_unassigned_nodes} unassigned nodes found\n")
        f.write(f"{len(updated_cluster_to_id_dict)} clusters remaining at the end\n")

        write_new_sorted_cluster_dict(updated_cluster_to_id_dict, unassigned_nodes, f"{output_prefix}/assign_unclustered_nodes_{cluster_criterion}_{min_degree}")



if __name__ == "__main__":
    assign_unclustered_nodes()
