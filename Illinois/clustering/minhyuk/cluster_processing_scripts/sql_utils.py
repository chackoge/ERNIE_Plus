import psycopg2


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
