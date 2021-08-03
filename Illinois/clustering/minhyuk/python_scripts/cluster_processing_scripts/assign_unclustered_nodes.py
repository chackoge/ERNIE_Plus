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
import psycopg2

from python_scripts.utils.utils import file_to_dict,save_scatter,write_new_sorted_cluster_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_intracluster_query_integer_id_indegree,get_intracluster_query_integer_id_outdegree,get_all_integer_ids


def find_best_cluster(current_id, cursor, table_name, cluster_to_id_dict, core_nodes, cluster_criterion):
    current_max_cluster = None
    current_max_value = 0
    for query_cluster,query_cluster_members in cluster_to_id_dict.items():
        core_query_cluster_members = list(set([int(cluster_member) for cluster_member in query_cluster_members]).intersection(core_nodes))
        current_value = 0
        if(cluster_criterion == "max_outdegree_to_c"):
            current_value += get_intracluster_query_integer_id_outdegree(cursor, table_name, current_id, core_query_cluster_members)
        elif(cluster_criterion == "max_indegree_to_c"):
            current_value += get_intracluster_query_integer_id_indegree(cursor, table_name, current_id, core_query_cluster_members)
        elif(cluster_criterion == "max_totaldegree_to_c"):
            current_value += get_intracluster_query_integer_id_outdegree(cursor, table_name, current_id, core_query_cluster_members)
            current_value += get_intracluster_query_integer_id_indegree(cursor, table_name, current_id, core_query_cluster_members)
        if(current_value > current_max_value):
            current_max_value = current_value
            current_max_cluster = query_cluster
    return {
        "best_cluster": current_max_cluster,
        "best_value": current_max_value,
    }


@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help="Clustering output from another method")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing postgres connection information")
@click.option("--core-nodes-file", required=True, type=click.Path(exists=True), help="The core nodes file containing the core nodes")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--cluster-criterion", required=True, type=click.Choice(["max_outdegree_to_c", "max_indegree_to_c", "max_totaldegree_to_c"]), help="Criterion to select which cluster a given unclustered node should be assigned to")
def assign_unclustered_nodes(clustering, config_file, core_nodes_file, output_prefix, cluster_criterion):
    '''This is the main command that takes in an input clustering and a network to assign unclustered nodes based on the criteria.
    The core nodes file should contain a node id for each line. The clustering file should be in a format "<cluster number>SPACE<node id>"
    The unassigned nodes will be assigned to a new cluster based on their indegree/outdegree/totaldegree to one of the clusters in the
    clustering that will maximuze the criterion.
    '''

    cluster_dicts = file_to_dict(clustering)
    cluster_to_id_dict = cluster_dicts["cluster_to_id_dict"]
    id_to_cluster_dict = cluster_dicts["id_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    updated_cluster_to_id_dict = cluster_to_id_dict.copy()
    print(f"{len(cluster_to_id_dict)} clusters to be looked through including singleton clusters")
    num_unassigned_nodes = 0
    all_ids = [str(node_id) for node_id in get_all_integer_ids(cursor, table_name)]
    unassigned_nodes = []
    print(f"{len(all_ids) - len(id_to_cluster_dict)} nodes without assignment")

    core_nodes = set()
    with open(core_nodes_file, "r") as f:
        for line in f:
            core_nodes.add(int(line.strip()))

    for current_id in all_ids:
        if(current_id not in id_to_cluster_dict):
            num_unassigned_nodes += 1
            # this is an unclustered node since it does not exist in our current clustering
            # we have picked the max cluster
            best_cluster_value_dict = find_best_cluster(current_id, cursor, table_name, cluster_to_id_dict, core_nodes, cluster_criterion)
            best_cluster = best_cluster_value_dict["best_cluster"]
            best_value  = best_cluster_value_dict["best_value"]

            if(best_value > 0):
                print(f"{current_id} went to {best_cluster} where it has {best_value} {cluster_criterion}")
                updated_cluster_to_id_dict[best_cluster].append(current_id)
            else:
                unassigned_nodes.append(current_id)
                print(f"{current_id} did not get assigned to anywhere based on the best value for {cluster_criterion} being {best_value}")

    print(f"{num_unassigned_nodes} unassigned nodes found")
    print(f"{len(updated_cluster_to_id_dict)} clusters remaining at the end")
    write_new_sorted_cluster_dict(updated_cluster_to_id_dict, unassigned_nodes, output_prefix + f"/assign_unclustered_nodes_{cluster_criterion}")



if __name__ == "__main__":
    assign_unclustered_nodes()
