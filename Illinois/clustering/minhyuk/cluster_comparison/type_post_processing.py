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

SMALL_SIZE = 12
MEDIUM_SIZE = 18
BIGGER_SIZE = 24

plt.rc("font", size=SMALL_SIZE)          # controls default text sizes
plt.rc("axes", titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc("axes", labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc("xtick", labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc("ytick", labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc("legend", fontsize=SMALL_SIZE)    # legend fontsize
plt.rc("figure", titlesize=BIGGER_SIZE)


def file_to_dict(clustering):
    cluster_to_doi_dict = {}
    doi_to_cluster_dict = {}

    with open(clustering, "r") as f:
        for current_line in f:
            [current_cluster_number, doi] = current_line.strip().split()
            if(int(current_cluster_number) not in cluster_to_doi_dict):
                cluster_to_doi_dict[int(current_cluster_number)] = []
            if(doi not in doi_to_cluster_dict):
                doi_to_cluster_dict[doi] = []
            cluster_to_doi_dict[int(current_cluster_number)].append(doi)
            doi_to_cluster_dict[doi].append(int(current_cluster_number))
    for current_doi in doi_to_cluster_dict:
        doi_to_cluster_dict[current_doi] = list(set(doi_to_cluster_dict[current_doi]))
    return {
        "cluster_to_doi_dict": cluster_to_doi_dict,
        "doi_to_cluster_dict": doi_to_cluster_dict,
    }


def get_cursor_client_dict(config_file):
    config = None
    with open(config_file, "r") as config_f:
        config = json.load(config_f)
    psql_connection_dict = {
        "dbname": config["dbname"],
        "user": config["user"],
    }
    psql_connection_string = " ".join("{}={}".format(psql_key, psql_connection_dict[psql_key]) for psql_key in psql_connection_dict)
    psql_connection=psycopg2.connect(psql_connection_string)
    cursor = psql_connection.cursor()
    return {
        "connection": psql_connection,
        "cursor": cursor,
    }


def get_intracluster_query_doi_indegree(cursor, doi, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT COUNT(DISTINCT citing) FROM europepmc_exosome_citations WHERE cited='{doi}' and citing in {cluster_member_string_representation}""")
    rows = cursor.fetchall()
    return rows[0][0]


def get_intracluster_query_doi_outdegree(cursor, doi, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT COUNT(DISTINCT cited) FROM europepmc_exosome_citations WHERE citing='{doi}' and cited in {cluster_member_string_representation}""")
    rows = cursor.fetchall()
    return rows[0][0]


def get_intracluster_query_doi_outgoing_dois(cursor, doi, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT DISTINCT cited FROM europepmc_exosome_citations WHERE citing='{doi}' and cited in {cluster_member_string_representation}""")
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]


def get_intracluster_doi_and_indegree(cursor, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT cited,COUNT(DISTINCT citing) FROM europepmc_exosome_citations WHERE citing in {cluster_member_string_representation} and cited in {cluster_member_string_representation} GROUP BY cited ORDER BY COUNT(DISTINCT citing) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]

def get_intracluster_doi_and_outdegree(cursor, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT citing,COUNT(DISTINCT cited) FROM europepmc_exosome_citations WHERE cited in {cluster_member_string_representation} and citing in {cluster_member_string_representation} GROUP BY citing ORDER BY COUNT(DISTINCT cited) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]

def get_all_incoming_dois(cursor, doi):
    cursor.execute(f"""SELECT DISTINCT citing FROM europepmc_exosome_citations WHERE cited='{doi}' """)
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]

def get_all_outgoing_dois(cursor, doi):
    cursor.execute(f"""SELECT DISTINCT cited FROM europepmc_exosome_citations WHERE citing='{doi}' """)
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]

def get_all_dois(cursor):
    cursor.execute(f"""SELECT DISTINCT citing FROM europepmc_exosome_citations UNION SELECT DISTINCT cited FROM europepmc_exosome_citations""")
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]

def get_all_doi_and_indegree(cursor):
    cursor.execute(f"""SELECT cited,COUNT(DISTINCT citing) FROM europepmc_exosome_citations GROUP BY cited ORDER BY COUNT(DISTINCT citing) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]

def get_all_doi_and_outdegree(cursor):
    cursor.execute(f"""SELECT citing,COUNT(DISTINCT cited) FROM europepmc_exosome_citations GROUP BY citing ORDER BY COUNT(DISTINCT cited) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]

def save_histogram(x_min, x_max, bin_size, data, y_label, x_label, title, output_prefix):
    plt.clf()
    plt.figure(figsize=(20, 17))
    bins = np.arange(x_min, x_max, bin_size)
    # plt.locator_params(nbins=10)
    plt.xticks(np.linspace(x_min, x_max, 25, dtype=int))
    plt.hist(data, bins=bins, density=False)
    plt.ylabel(y_label)
    plt.xlabel(x_label);
    plt.title(title);
    plt.savefig(output_prefix + ".png", bbox_inches="tight")
    plt.close()


def save_scatter(x_data, y_data, x_label, y_label, title, output_prefix, y_min=0, add_x_y_line=False, log_log=False):
    # plt.locator_params(nbins=10)
    plt.clf()
    plt.figure(figsize=(20, 17))
    plt.xticks(np.linspace(0, max(x_data), 25, dtype=int))
    plt.scatter(x_data, y_data)
    if(add_x_y_line):
        print("adding y=x")
        plt.plot(x_data, x_data, color="red", label="y=x")
    plt.ylim(ymin=y_min)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig(output_prefix + ".png", bbox_inches="tight")
    plt.close()

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
    elif(method == "scatter_plot_indegrees"):
        scatter_plot_indegrees(clustering, config_file, output_prefix, figure_prefix)


def scatter_plot_indegrees(clustering, config_file, output_prefix, figure_prefix):
    cluster_dicts = file_to_dict(clustering)
    cluster_to_doi_dict = cluster_dicts["cluster_to_doi_dict"]
    doi_to_cluster_dict = cluster_dicts["doi_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    num_dois = len(get_all_dois(cursor))

    print(f"num_dois: {num_dois}")
    print(f"num_clusters: {len(cluster_to_doi_dict)}")
    indegree_dict = {}
    indegree_from_own_cluster_dict = {}
    for doi,cited_by_count in get_all_doi_and_indegree(cursor)[:10000]:
        indegree_dict[doi] = cited_by_count
        indegree_from_own_cluster_dict[doi] = 0
        for current_cluster_number in doi_to_cluster_dict[doi]:
            if(len(doi_to_cluster_dict[doi]) > 1):
                print(f"Overlapping clustering detected")
            cluster_member_arr = cluster_to_doi_dict[current_cluster_number]
            indegree_from_own_cluster_dict[doi] += get_intracluster_query_doi_indegree(cursor, doi, cluster_member_arr)
    print(f"computed indegrees")
    outdegree_dict = {}
    outdegree_to_own_cluster_dict = {}
    for doi,citing_count in get_all_doi_and_outdegree(cursor)[:10000]:
        outdegree_dict[doi] = citing_count
        outdegree_to_own_cluster_dict[doi] = 0
        for current_cluster_number in doi_to_cluster_dict[doi]:
            if(len(doi_to_cluster_dict[doi]) > 1):
                print(f"Overlapping clustering detected")
            cluster_member_arr = cluster_to_doi_dict[current_cluster_number]
            outdegree_to_own_cluster_dict[doi] += get_intracluster_query_doi_outdegree(cursor, doi, cluster_member_arr)
    print(f"computed outdegrees")

    indegree_scatter_x_data = []
    indegree_scatter_y_data = []
    outdegree_scatter_x_data = []
    outdegree_scatter_y_data = []
    for doi in indegree_dict:
        indegree_scatter_x_data.append(indegree_from_own_cluster_dict[doi])
        indegree_scatter_y_data.append(indegree_dict[doi])

    for doi in outdegree_dict:
        outdegree_scatter_x_data.append(outdegree_to_own_cluster_dict[doi])
        outdegree_scatter_y_data.append(outdegree_dict[doi])

    save_scatter(indegree_scatter_x_data, indegree_scatter_y_data, "indegree from the cluster the publication belongs to", "indegree from the entire network", "total to cluster indegrees", f"{figure_prefix}/total_membership_indegree", add_x_y_line=True)
    save_scatter(outdegree_scatter_x_data, outdegree_scatter_y_data, "outdegree to the cluster the publication belongs to", "outdegree to the entire network", "total to cluster outdegrees", f"{figure_prefix}/total_membership_outdegree", add_x_y_line=True)


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
