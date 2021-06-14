"""An example program that uses the elsapy module"""
import urllib
import multiprocessing

import click
import json
import psycopg2

from api import elsentity
from api import elsclient
from api import elsdoc

def wait_n_minutes(n):
    sleep(n * 60)

def get_bibliography(extended_abs_doc):
    bibliography = []
    raw_list = extended_abs_doc.data["item"]["bibrecord"]["tail"]["bibliography"]["reference"]
    for reference in raw_list:
        current_item = reference["ref-info"]["refd-itemidlist"]["itemid"]
        bibliography.append((current_item["@idtype"], current_item["$"]))
    return bibliography

def query_api(client, input_doi_queue, results_doi_queue, timeout):
    doi = input_doi_queue.get(timeout=timeout)
    extended_abs_doc = elsdoc.ExtendedAbsDoc(doi=doi)
    client.logger.info(extended_abs_doc.int_id())
    if extended_abs_doc.read(client):
        extended_abs_doc.write()
        results_doi_queue.put(doi)
        new_doc = elsdoc.ExtendedAbsDoc(doi=doi)
        new_doc.read_json(new_doc.get_datapath())
        client.logger.info(new_doc.int_id())

def run_doi_search(config_file, secrets_file, num_processes):
    cursor_client_dict = get_cursor_client_dict(config_file, secrets_file)
    cursor = cursor_client_dict["cursor"]
    client = cursor_client_dict["client"]

    pool = multiprocessing.Pool(processes=num_processes)
    manager = multiprocessing.Manager()

    api_fetch_size_per_minute = 25
    transaction_batch_size = 20
    retry = 0
    retry_limit = 3
    timeout_limit = 300

    input_doi_queue = manager.Queue()
    results_doi_queue = manager.Queue()
    pool.apply_async(query_api, (client, input_doi_queue, results_doi_queue, timeout_limit * retry_limit))

    while(retry < retry_limit):
        wait_n_minutes(1)
        current_input_queue_size = input_doi_queue.qsize()
        fetch_from_db_size = api_fetch_size_per_minute - current_input_queue_size
        if(fetch_from_db_size > 0):
            # intecsect the two tables and get the dois
            # cursor.execute("SELECT COUNT(*) FROM (SELECT DISTINCT citing FROM europepmc_exosome_citations UNION SELECT DISTINCT cited FROM europepmc_exosome_citations) AS uniont")
            # rows = cursor.fetchall()
               # push the dois into the input_doi_queue

        timeout = 0
        while(results_doi_queue.qsize() < transaction_batch_size):
            if(timeout == timeout_limit):
                retry += 1
                break
            sleep(1)
            timeout += 1

        if(timeout != timeout_limit):
            retry = 0
            # pull from results_doi_queue into a local varibale
            # INSERT into the new database
            # file_location = client.output_dir + str(doi) + '.json'


def get_cursor_client_dict(config_file, secrets_file):
    secrets = None
    config = None
    with open(secrets_file, "r") as secrets_f:
        secrets = json.load(secrets_f)
    with open(config_file, "r") as config_f:
        config = json.load(config_f)
    psql_connection_dict = {
        "dbname": config["dbname"],
        "user": config["user"],
    }
    backbone_dbname = config["backbonedb"]
    psql_connection_string = " ".join("{}={}".format(psql_key, psql_connection_dict[psql_key]) for psql_key in psql_connection_dict)
    psql_connection=psycopg2.connect(psql_connection_string)
    cursor = psql_connection.cursor()
    api_key = secrets["apikey"]
    inst_token = secrets["insttoken"]
    output_dir = config["output_dir"]
    log_dir = config["log_dir"]
    client = elsclient.ElsClient(api_key=api_key, inst_token=inst_token, output_dir=output_dir, log_dir=log_dir)
    return {
        "cursor": cursor,
        "client": client,
    }

@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the backbonedb and processeddb")
@click.option("--secrets-file", required=True, type=click.Path(exists=True), help="The secrets file containing the api keys")
@click.option("--num-processes", required=False, type=int, default=1, help="Number of Workers")
def doi_search(config_file, secrets_file, num_processes):
    run_doi_search()
