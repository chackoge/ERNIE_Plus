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


@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help="Clustering output from another method")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the backbonedb and processeddb")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--method", required=True, type=click.Choice(["increment_type_1", "increment_type_1+plot", "scatter_plot_indegrees"]))
def type_post_processing(clustering, config_file, output_prefix, figure_prefix, method):
    if(method == "increment_type_1"):
        increment_type_one(clustering, config_file, output_prefix, figure_prefix, False)
    elif(method == "increment_type_1+plot"):
        increment_type_one(clustering, config_file, output_prefix, figure_prefix, True)

def increment_type_one(clustering, config_file, output_prefix, figure_prefix, generate_histogram):
    cluster_dicts = file_to_dict(clustering)
    cluster_to_doi_dict = cluster_dicts["cluster_to_doi_dict"]
    doi_to_cluster_dict = cluster_dicts["doi_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    highly_cited_doi_arr = []
    num_dois = len(get_all_dois(cursor))

    # highly_cited_threshold = 0.00001 # gets about 4 publications?
    highly_cited_threshold = 0.0001
    type_1_threshold = 0.1

    print(f"num_dois: {num_dois}")
    print(f"num_clusters: {len(cluster_to_doi_dict)}")
    incoming_node_degree_dict = {}
    for doi,cited_by_count in get_all_doi_and_indegree(cursor):
        incoming_node_degree_dict[doi] = cited_by_count
        if(len(highly_cited_doi_arr) < num_dois * highly_cited_threshold):
            highly_cited_doi_arr.append(doi)
    print(f"top {highly_cited_threshold} nodes by indegree: {highly_cited_doi_arr}")

    cluster_type_1_threshold_dict = {}
    type_1_to_be_updated = {}
    histogram_data_cluster_indegrees = {}
    histogram_data_cluster_outdegrees = {}
    histogram_data_highly_cited_doi_in_out_degrees = {}

    for highly_cited_doi in highly_cited_doi_arr: # DEBUG: cropping at :1 to make it faster and not look through all the highly cited nodes
        current_incoming_dois = get_all_incoming_dois(cursor, highly_cited_doi)
        print(f"{len(current_incoming_dois)} incoming dois")
        print(f"belongs to {doi_to_cluster_dict[highly_cited_doi]}")
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
            histogram_data_cluster_indegrees[highly_cited_doi] = {}
            histogram_data_cluster_outdegrees[highly_cited_doi] = {}

        for current_incoming_cluster_number in current_incoming_clusters_arr:
            if(current_incoming_cluster_number not in cluster_type_1_threshold_dict):
                current_intracluster_doi_and_indegree_arr = get_intracluster_doi_and_indegree(cursor, cluster_to_doi_dict[current_incoming_cluster_number])
                current_intracluster_doi_and_outdegree_arr = get_intracluster_doi_and_outdegree(cursor, cluster_to_doi_dict[current_incoming_cluster_number])

                if(generate_histogram):
                    histogram_data_cluster_indegrees[highly_cited_doi][current_incoming_cluster_number] = [int(tup[1]) for tup in current_intracluster_doi_and_indegree_arr]
                    histogram_data_cluster_outdegrees[highly_cited_doi][current_incoming_cluster_number] = [int(tup[1]) for tup in current_intracluster_doi_and_outdegree_arr]

                if(len(current_intracluster_doi_and_indegree_arr) == 0):
                    cluster_type_1_threshold_dict[current_incoming_cluster_number] = 0
                    print(f"cluster {current_incoming_cluster_number} has {len(cluster_to_doi_dict[current_incoming_cluster_number])} members but has 0 intracluster indegree")
                else:
                    cluster_type_1_threshold_dict[current_incoming_cluster_number] = int(current_intracluster_doi_and_indegree_arr[int(len(current_intracluster_doi_and_indegree_arr) * type_1_threshold)][1])
            cluster_member_arr = cluster_to_doi_dict[current_incoming_cluster_number]
            current_highly_cited_doi_indegree = get_intracluster_query_doi_indegree(cursor, highly_cited_doi, cluster_member_arr)
            current_highly_cited_doi_outdegree = get_intracluster_query_doi_outdegree(cursor, highly_cited_doi, cluster_member_arr)
            current_highly_cited_doi_outgoing_dois = get_intracluster_query_doi_outgoing_dois(cursor, highly_cited_doi, cluster_member_arr)

            if(generate_histogram):
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["x"].append(current_incoming_cluster_number)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["indegree"]["y"].append(current_highly_cited_doi_indegree)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["x"].append(current_incoming_cluster_number)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["outdegree"]["y"].append(current_highly_cited_doi_outdegree)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["x"].append(current_incoming_cluster_number)
                histogram_data_highly_cited_doi_in_out_degrees[highly_cited_doi]["sumdegree"]["y"].append(current_highly_cited_doi_indegree + current_highly_cited_doi_outdegree)

            if(current_highly_cited_doi_indegree > cluster_type_1_threshold_dict[current_incoming_cluster_number] and
                current_incoming_cluster_number not in doi_to_cluster_dict[highly_cited_doi]):
                print(f"UPDATE: {highly_cited_doi} has indegree {current_highly_cited_doi_indegree} and outdegree {current_highly_cited_doi_outdegree}({current_highly_cited_doi_outgoing_dois}) in cluster {current_incoming_cluster_number} where the top {type_1_threshold}th indegree is {cluster_type_1_threshold_dict[current_incoming_cluster_number]}")
                if(highly_cited_doi not in type_1_to_be_updated):
                    type_1_to_be_updated[highly_cited_doi] = []
                type_1_to_be_updated[highly_cited_doi].append(current_incoming_cluster_number)
    print(cluster_type_1_threshold_dict)
    print(type_1_to_be_updated)

    for highly_cited_doi in type_1_to_be_updated:
        for cluster_number in type_1_to_be_updated[highly_cited_doi]:
            cluster_to_doi_dict[cluster_number].append(highly_cited_doi)
    with open(f"{output_prefix}/incremented.clustering", "w") as f:
        for cluster_number in range(max(cluster_to_doi_dict.keys())):
            if(cluster_number in cluster_to_doi_dict):
                for cluster_member_doi in cluster_to_doi_dict[cluster_number]:
                    f.write(f"{cluster_number} {cluster_member_doi}\n")

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

        print(f"saved degree scatter plots")
        for highly_cited_doi in highly_cited_doi_arr[:1]:
            for cluster_number in histogram_data_cluster_indegrees[highly_cited_doi]:
                if(len(histogram_data_cluster_indegrees[highly_cited_doi][cluster_number]) > 0):
                    save_histogram(0, max(histogram_data_cluster_indegrees[highly_cited_doi][cluster_number]) + 1, 1, histogram_data_cluster_indegrees[highly_cited_doi][cluster_number], "count", "intracluster indegrees", f"cluster number: {cluster_number}", f"{figure_prefix}/{highly_cited_doi.replace('/', 'SLASH')}_{cluster_number}_intracluster_indegrees")
            for cluster_number in histogram_data_cluster_outdegrees[highly_cited_doi]:
                if(len(histogram_data_cluster_outdegrees[highly_cited_doi][cluster_number]) > 0):
                    save_histogram(0, max(histogram_data_cluster_outdegrees[highly_cited_doi][cluster_number]) + 1, 1, histogram_data_cluster_outdegrees[highly_cited_doi][cluster_number], "count", "intracluster outdegrees", f"cluster number: {cluster_number}", f"{figure_prefix}/{highly_cited_doi.replace('/', 'SLASH')}_{cluster_number}_intracluster_outdegrees")
        print(f"saved cluster histograms")

if __name__ == "__main__":
    type_post_processing()
