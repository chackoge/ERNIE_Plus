import json

import psycopg2


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
        "table_name": config["table_name"],
    }


def get_intracluster_query_doi_indegree(cursor, table_name, doi, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT COUNT(DISTINCT citing) FROM {table_name} WHERE cited='{doi}' and citing in {cluster_member_string_representation}""")
    rows = cursor.fetchall()
    return rows[0][0]


def get_intracluster_query_doi_outdegree(cursor, table_name, doi, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT COUNT(DISTINCT cited) FROM {table_name} WHERE citing='{doi}' and cited in {cluster_member_string_representation}""")
    rows = cursor.fetchall()
    return rows[0][0]


def get_intracluster_query_doi_outgoing_dois(cursor, table_name, doi, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT DISTINCT cited FROM {table_name} WHERE citing='{doi}' and cited in {cluster_member_string_representation}""")
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]


def get_intracluster_doi_and_indegree(cursor, table_name, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT cited,COUNT(DISTINCT citing) FROM {table_name} WHERE citing in {cluster_member_string_representation} and cited in {cluster_member_string_representation} GROUP BY cited ORDER BY COUNT(DISTINCT citing) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]


def get_intracluster_doi_and_outdegree(cursor, table_name, cluster_member_arr):
    if(len(cluster_member_arr) < 1):
        return []
    cluster_member_string_representation = "("
    cluster_member_string_representation += ("'" + cluster_member_arr[0] + "'")
    for cluster_member in cluster_member_arr[1:]:
        cluster_member_string_representation += ("," + "'" + cluster_member + "'")
    cluster_member_string_representation += ")"
    cursor.execute(f"""SELECT citing,COUNT(DISTINCT cited) FROM {table_name} WHERE cited in {cluster_member_string_representation} and citing in {cluster_member_string_representation} GROUP BY citing ORDER BY COUNT(DISTINCT cited) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]


def get_all_incoming_dois(cursor, table_name, doi):
    cursor.execute(f"""SELECT DISTINCT citing FROM {table_name} WHERE cited='{doi}' """)
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]


def get_all_outgoing_dois(cursor, table_name, doi):
    cursor.execute(f"""SELECT DISTINCT cited FROM {table_name} WHERE citing='{doi}' """)
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]


def get_all_dois(cursor, table_name):
    cursor.execute(f"""SELECT DISTINCT citing FROM {table_name} UNION SELECT DISTINCT cited FROM {table_name}""")
    rows = cursor.fetchall()
    return [tup[0] for tup in rows]


def get_all_doi_and_indegree(cursor, table_name):
    cursor.execute(f"""SELECT cited,COUNT(DISTINCT citing) FROM {table_name} GROUP BY cited ORDER BY COUNT(DISTINCT citing) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]


def get_all_doi_and_outdegree(cursor, table_name):
    cursor.execute(f"""SELECT citing,COUNT(DISTINCT cited) FROM {table_name} GROUP BY citing ORDER BY COUNT(DISTINCT cited) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]


def get_all_id_and_indegree(cursor, table_name):
    cursor.execute(f"""SELECT cited_id,COUNT(DISTINCT citing_id) FROM {table_name} GROUP BY cited_id ORDER BY COUNT(DISTINCT citing_id) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]


def get_all_id_and_outdegree(cursor, table_name):
    cursor.execute(f"""SELECT citing_id,COUNT(DISTINCT cited_id) FROM {table_name} GROUP BY citing_id ORDER BY COUNT(DISTINCT cited_id) DESC""")
    rows = cursor.fetchall()
    return [tup for tup in rows]
