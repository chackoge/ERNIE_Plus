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

from utils import file_to_dict,save_scatter
from sql_utils import get_cursor_client_dict,get_all_dois,get_all_doi_and_indegree,get_all_incoming_dois,get_intracluster_doi_and_indegree,get_intracluster_query_doi_indegree,get_intracluster_query_doi_outdegree

def write_new_clustering_file(type_1_to_be_updated, cluster_to_doi_dict, output_prefix):
    '''This function takes in a dictionary of type 1 nodes to be updated to the list of clusters they newly belong to
    and the original clustering to output a new overlapping clustering where each line is "<cluster number>SPACE<node id>"
    and multiple memberships are simply represented with additional rows of identical node ids and different cluster numbers.
    '''
    for highly_cited_doi in type_1_to_be_updated:
        for cluster_number in type_1_to_be_updated[highly_cited_doi]:
            cluster_to_doi_dict[cluster_number].append(highly_cited_doi)
    with open(f"{output_prefix}/incremented.clustering", "w") as f:
        for cluster_number in range(max(cluster_to_doi_dict.keys())):
            if(cluster_number in cluster_to_doi_dict):
                for cluster_member_doi in cluster_to_doi_dict[cluster_number]:
                    f.write(f"{cluster_number} {cluster_member_doi}\n")


@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help="Clustering output from another method")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the backbonedb and processeddb")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--figure-prefix", required=False, type=click.Path(), help="Output figure prefix")
@click.option("--highly-cited-threshold", required=False, type=float, default=0.0001, help="Threshold for the entire network on what is a highly cited publication")
@click.option("--type-1-threshold", required=False, type=float, default=0.1, help="Threshold for a a cluster on what is a type 1 node")
@click.option("--method", required=True, type=click.Choice(["increment_type_1", "increment_type_1+plot"]))
def type_post_processing(clustering, config_file, output_prefix, figure_prefix, highly_cited_threshold, type_1_threshold, method):
    '''This is the main function that will take in an input clustering of the format "<cluster number>SPACE<node id>"
    and output an overlapping clustering by taking all the nodes with indegree greater than the top highly_cited_threshold-th percentile and
    add the node to a cluster if the indegree from that cluster to the node is greater than the top type_1_threshold-th percentile within that cluster.
    the +plot option will simply add scatter plots. Currently, for every highly cited node, two scatter plots are generated
    where the x axis is the cluster number, y axis is the in/outdegree from the cluster.

    in pseudocode, it is as follows:
    1 Process the high degree nodes (at a network level) in turn.
        2 Examine all of the publications that cite A, the current high degree node.
        3 Identify the clusters of each of the publications that cite A.
        4 For each cluster identified in the previous step
            4a If hasn't been computed already, calculate the "type 1" threshold (not all clusters need type 1 thresholds computed).
            4b If A is cited by a sufficient number of publications in this cluster, add A to this cluster.
    Note: Don't recompute the type 1 threshold even though the cluster membership has been updated
    '''
    if(method == "increment_type_1"):
        increment_type_one(clustering, config_file, output_prefix, figure_prefix, highly_cited_threshold, type_1_threshold, False)
    elif(method == "increment_type_1+plot"):
        increment_type_one(clustering, config_file, output_prefix, figure_prefix, highly_cited_threshold, type_1_threshold, True)

def increment_type_one(clustering, config_file, output_prefix, figure_prefix, highly_cited_threshold, type_1_threshold, generate_histogram):
    cluster_dicts = file_to_dict(clustering)
    cluster_to_doi_dict = cluster_dicts["cluster_to_doi_dict"]
    doi_to_cluster_dict = cluster_dicts["doi_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    highly_cited_doi_arr = []
    num_dois = len(get_all_dois(cursor, table_name))

    print(f"num_dois: {num_dois}")
    print(f"num_clusters: {len(cluster_to_doi_dict)}")
    # this for loop determines which nodes are the highly cited nodes in the network
    incoming_node_degree_dict = {}
    for doi,cited_by_count in get_all_doi_and_indegree(cursor, table_name):
        incoming_node_degree_dict[doi] = cited_by_count
        if(len(highly_cited_doi_arr) < num_dois * highly_cited_threshold):
            highly_cited_doi_arr.append(doi)
    print(f"top {highly_cited_threshold} nodes by indegree: {highly_cited_doi_arr}")

    cluster_type_1_threshold_dict = {}
    type_1_to_be_updated = {}
    histogram_data_highly_cited_doi_in_out_degrees = {}

    # this is step 1 in the pseudocode
    for highly_cited_doi in highly_cited_doi_arr:
        # this is step 2 in the pseudocode
        current_incoming_dois = get_all_incoming_dois(cursor, table_name, highly_cited_doi)
        print(f"{len(current_incoming_dois)} incoming dois")
        print(f"belongs to {doi_to_cluster_dict[highly_cited_doi]}")
        # this current_incoming_cluters array represents all the clusters has at least one publication that cites the highly cited node
        # this is step 3 in the pseudocode
        current_incoming_clusters_arr = list(reduce(lambda x,y: x.union(set(doi_to_cluster_dict[y])), current_incoming_dois, set()))
        current_incoming_clusters_arr.sort()
        print(f"{highly_cited_doi} is cited by dois from {len(current_incoming_clusters_arr)} clusters ({current_incoming_clusters_arr})")

        if(generate_histogram):
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi] = {}
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["membership"] = doi_to_cluster_dict[highly_cited_doi]
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"] = {}
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"] = {}
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"] = {}
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["x"] = []
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["y"] = []
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["x"] = []
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["y"] = []
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["x"] = []
            histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["y"] = []

        # this is step 4 in the pseudocode
        for current_incoming_cluster_number in current_incoming_clusters_arr:
            # this is step 4a in the pseudocode
            if(current_incoming_cluster_number not in cluster_type_1_threshold_dict):
                # type 1 thresholds are computed as needed by looking at the sorted list of intracluster indegrees and taking the
                # top type_1_threshold-th percentile's indegree. Any node must exceed this threshold in order to be considered a type 1 node is this cluter
                current_intracluster_doi_and_indegree_arr = get_intracluster_doi_and_indegree(cursor, table_name, cluster_to_doi_dict[current_incoming_cluster_number])
                if(len(current_intracluster_doi_and_indegree_arr) == 0):
                    print(f"cluster {current_incoming_cluster_number} has {len(cluster_to_doi_dict[current_incoming_cluster_number])} members but has 0 intracluster indegree")
                    cluster_type_1_threshold_dict[current_incoming_cluster_number] = 0
                else:
                    cluster_type_1_threshold_dict[current_incoming_cluster_number] = int(current_intracluster_doi_and_indegree_arr[int(len(current_intracluster_doi_and_indegree_arr) * type_1_threshold)][1])
            cluster_member_arr = cluster_to_doi_dict[current_incoming_cluster_number]
            current_highly_cited_doi_indegree = get_intracluster_query_doi_indegree(cursor, table_name, highly_cited_doi, cluster_member_arr)
            # here we compare the indegree of the current publication from the cluster and the type 1 threshold for that cluster
            # this is step 4b in the pseudocode
            if(current_highly_cited_doi_indegree > cluster_type_1_threshold_dict[current_incoming_cluster_number] and
                current_incoming_cluster_number not in doi_to_cluster_dict[highly_cited_doi]):
                print(f"UPDATE: {highly_cited_doi} has indegree {current_highly_cited_doi_indegree} in cluster {current_incoming_cluster_number} where the top {type_1_threshold}th indegree is {cluster_type_1_threshold_dict[current_incoming_cluster_number]}")
                # this is one of the relevant sections for the note portion in the pseudocode
                if(highly_cited_doi not in type_1_to_be_updated):
                    type_1_to_be_updated[highly_cited_doi] = []
                type_1_to_be_updated[highly_cited_doi].append(current_incoming_cluster_number)

            if(generate_histogram):
                current_highly_cited_doi_outdegree = get_intracluster_query_doi_outdegree(cursor, table_name, highly_cited_doi, cluster_member_arr)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["x"].append(current_incoming_cluster_number)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["y"].append(current_highly_cited_doi_indegree)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["x"].append(current_incoming_cluster_number)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["y"].append(current_highly_cited_doi_outdegree)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["x"].append(current_incoming_cluster_number)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["y"].append(current_highly_cited_doi_indegree + current_highly_cited_doi_outdegree)

    # this is one of the relevant sections for the note portion in the pseudocode
    write_new_clustering_file(type_1_to_be_update, cluster_to_doi_dict, output_prefix)

    if(generate_histogram):
        for highly_cited_doi in highly_cited_doi_arr[:1]:
            x_indegree_data = histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["x"]
            y_indegree_data = histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["y"]
            x_outdegree_data = histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["x"]
            y_outdegree_data = histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["y"]
            x_sumdegree_data = histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["x"]
            y_sumdegree_data = histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["y"]
            save_scatter(x_indegree_data, y_indegree_data, "cluster number", "indegree from the cluster", f"node: {highly_cited_doi}", f"{figure_prefix}/{highly_cited_doi.replace('/','SLASH')}_indegree", y_min=1)
            save_scatter(x_outdegree_data, y_outdegree_data, "cluster number", "outdegree from the cluster", f"node: {highly_cited_doi}", f"{figure_prefix}/{highly_cited_doi.replace('/','SLASH')}_outdegree", y_min=1)
            save_scatter(x_sumdegree_data, y_sumdegree_data, "cluster number", "sumdegree from the cluster", f"node: {highly_cited_doi}", f"{figure_prefix}/{highly_cited_doi.replace('/','SLASH')}_sumdegree", y_min=1)


if __name__ == "__main__":
    type_post_processing()
