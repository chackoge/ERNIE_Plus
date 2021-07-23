import json

import click
import psycopg2


def file_to_dict(clustering):
    '''This function takes in an input clustering of format "<cluster number>SPACE<node id>"
    and returns two python dictionaries that map from cluster number to a list of node ids and
    from a node id to list of cluster numbers.
    '''
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
    '''This function parses a JSON formatted config file
    that contains the dbname, username, and table name to return a
    psycopg2 connection and cursor.
    '''
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
        "table_name": config["tablename"],
    }


def get_sum_degrees(cursor, k, table_name):
    '''This is a SQL wrapper that takes in a node degree and returns
    all nodes with degree k.
    '''
    cursor.execute(f"""with outdegree_table as (
    select citing as node, count(distinct cited) as degree from {table_name} group by citing order by count(distinct cited) desc
    ), indegree_table as (
    select cited as node, count(distinct citing) as degree from {table_name} group by cited order by count(distinct citing) desc
    ), sumdegree_table as (
    select node, degree from outdegree_table
    union
    select node, degree from indegree_table
    ), node_sum_table as (
    select node, sum(degree) from sumdegree_table group by node order by sum(degree) desc
    )
    select node,sum from node_sum_table where sum = {k} """)
    rows = cursor.fetchall()
    return [tup for tup in rows]


def delete_doi_array(connection, cursor, doi_arr, table_name):
    '''This is a SQL wrapper that takes in a list of dois and drops rows that
    include the doi.
    '''
    doi_arr_string_representation = "("
    doi_arr_string_representation += ("'" + doi_arr[0] + "'")
    for doi in doi_arr[1:]:
        doi_arr_string_representation += ("," + "'" + doi + "'")
    doi_arr_string_representation += ")"
    cursor.execute(f"""DELETE FROM {table_name} WHERE citing IN {doi_arr_string_representation} OR cited IN {doi_arr_string_representation}""")
    connection.commit()


@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the backbonedb and processeddb")
@click.option("--k", required=True, type=int, help="Nodes with degree k will be removed")
def remove_degree_k(config_file, k):
    '''This is the main function that takes in a config file containing database information
    and removes every node with degree k
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    dois_to_delete = [tup[0] for tup in get_sum_degrees(cursor, 3, table_name)]
    delete_doi_array(connection, cursor, dois_to_delete, table_name)


if __name__ == "__main__":
    # create your own table first like
    # SELECT * INTO <your table name without spaces hopefully> FROM europepmc_exosomes_citations;
    remove_degree_k()
