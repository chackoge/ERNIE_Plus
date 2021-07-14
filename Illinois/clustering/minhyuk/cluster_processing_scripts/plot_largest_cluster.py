import click
import numpy as np

from utils import file_to_dict,save_histogram
from sql_utils import get_cursor_client_dict,get_intracluster_doi_and_indegree,get_intracluster_doi_and_outdegree


@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help="Clustering output from another method")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Output file prefix")
def plot_largest_cluster_in_out_degrees(clustering, config_file, output_prefix, figure_prefix):
    '''This is the main function that will taken in a clustering and a config file
    and write a histogram of the biggeest cluster's intracluster indgree and outdegrees
    '''
    cluster_dicts = file_to_dict(clustering)
    cluster_to_doi_dict = cluster_dicts["cluster_to_doi_dict"]
    doi_to_cluster_dict = cluster_dicts["doi_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    largest_cluster_number = list(cluster_to_doi_dict.keys())[0]
    for cluster_number in cluster_to_doi_dict:
        if(len(cluster_to_doi_dict[cluster_number]) > len(cluster_to_doi_dict[largest_cluster_number])):
            largest_cluster_number = cluster_number

    print(f"the largest cluster number is {largest_cluster_number} with size {len(cluster_to_doi_dict[largest_cluster_number])}")
    current_intracluster_doi_and_indegree_arr = get_intracluster_doi_and_indegree(cursor, cluster_to_doi_dict[largest_cluster_number])
    current_intracluster_doi_and_outdegree_arr = get_intracluster_doi_and_outdegree(cursor, cluster_to_doi_dict[largest_cluster_number])
    histogram_indegree_data = [int(tup[1]) for tup in current_intracluster_doi_and_indegree_arr]
    histogram_outdegree_data = [int(tup[1]) for tup in current_intracluster_doi_and_outdegree_arr]
    print(f"number of nodes in indegree data: {len(histogram_indegree_data)}")
    print(f"number of nodes in outdegree data: {len(histogram_outdegree_data)}")
    maximum_indegree_index = np.argmax(histogram_indegree_data)
    maximum_outdegree_index = np.argmax(histogram_outdegree_data)
    print(f"node with the highest indegree is {current_intracluster_doi_and_indegree_arr[maximum_indegree_index]}")
    print(f"node with the highest outdegree is {current_intracluster_doi_and_outdegree_arr[maximum_outdegree_index]}")
    return
    save_histogram(0, max(histogram_indegree_data) + 1, 1, histogram_indegree_data, "count", "intracluster indegrees", f"cluster number: {largest_cluster_number}", f"{figure_prefix}/{largest_cluster_number}_intracluster_indegrees")
    save_histogram(0, max(histogram_outdegree_data) + 1, 1, histogram_outdegree_data, "count", "intracluster outdegrees", f"cluster number: {largest_cluster_number}", f"{figure_prefix}/{largest_cluster_number}_intracluster_outdegrees")

if __name__ == "__main__":
    plot_largest_cluster_in_and_degrees()
