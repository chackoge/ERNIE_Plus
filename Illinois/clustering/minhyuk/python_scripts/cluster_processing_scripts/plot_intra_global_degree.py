import click

from utils import file_to_dict,save_scatter
from sql_utils import get_cursor_client_dict,get_intracluster_query_doi_indegree,get_intracluster_query_doi_outdegree,get_all_dois,get_all_doi_and_indgree,get_all_doi_and_outdegree

@click.command()
@click.option("--clustering", required=True, type=click.Path(exists=True), help="Clustering output from another method")
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Output file prefix")
def plot_intra_global_degree(clustering, config_file, output_prefix, figure_prefix):
    '''This function takes in a clustering output of the format "<cluster number>SPACE<node id>"
    and writes a scatter plot of intracluster indgree to global indegree for every publication, and does the same
    for the outdegrees as well.
    '''
    cluster_dicts = file_to_dict(clustering)
    cluster_to_doi_dict = cluster_dicts["cluster_to_doi_dict"]
    doi_to_cluster_dict = cluster_dicts["doi_to_cluster_dict"]
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    num_dois = len(get_all_dois(cursor, table_name))

    print(f"num_dois: {num_dois}")
    print(f"num_clusters: {len(cluster_to_doi_dict)}")
    indegree_dict = {}
    indegree_from_own_cluster_dict = {}
    # currently it only takes in the top 10,000 nodes in terms of indegree to save time
    for doi,cited_by_count in get_all_doi_and_indegree(cursor)[:10000]:
        indegree_dict[doi] = cited_by_count
        indegree_from_own_cluster_dict[doi] = 0
        for current_cluster_number in doi_to_cluster_dict[doi]:
            if(len(doi_to_cluster_dict[doi]) > 1):
                print(f"Overlapping clustering detected")
            cluster_member_arr = cluster_to_doi_dict[current_cluster_number]
            indegree_from_own_cluster_dict[doi] += get_intracluster_query_doi_indegree(cursor, table_name, doi, cluster_member_arr)
    print(f"computed indegrees")
    outdegree_dict = {}
    outdegree_to_own_cluster_dict = {}
    # currently it only takes in the top 10,000 nodes in terms of outdpgree to save time
    for doi,citing_count in get_all_doi_and_outdegree(cursor, table_name)[:10000]:
        outdegree_dict[doi] = citing_count
        outdegree_to_own_cluster_dict[doi] = 0
        for current_cluster_number in doi_to_cluster_dict[doi]:
            if(len(doi_to_cluster_dict[doi]) > 1):
                print(f"Overlapping clustering detected")
            cluster_member_arr = cluster_to_doi_dict[current_cluster_number]
            outdegree_to_own_cluster_dict[doi] += get_intracluster_query_doi_outdegree(cursor, table_name, doi, cluster_member_arr)
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


if __name__ == "__main__":
    plot_intra_global_degree()
