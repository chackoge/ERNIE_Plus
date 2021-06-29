"""An example program that uses the elsapy module"""
import urllib
import multiprocessing
import queue
import sys
import traceback
import time

import click
import json
import psycopg2

from api import elsentity
from api import elssearch
from api import elsclient
from api import elsdoc


DEBUG = True
# DEBUG = False

def wait_n_minutes(n):
    time.sleep(n * 60)

def query_api(cursor_client_dict, input_doi_queue, results_doi_queue, timeout):
    client = elsclient.ElsClient(**cursor_client_dict)
    client.logger.info("worker started")
    while(True):
        try:
            doi = input_doi_queue.get(timeout=timeout)
            client.logger.info("worker:" + str(multiprocessing.current_process()) + " processing " + str(doi))
            extended_abs_doc = elsdoc.ExtendedAbsDoc(doi=doi)
            if extended_abs_doc.read(client):
                if(DEBUG):
                    print(f"{doi}: document written")
                extended_abs_doc.write()
                sgr = extended_abs_doc.int_id
                bibliography = extended_abs_doc.get_bibliography()
                client.logger.info(sgr + " is located at " + str(extended_abs_doc.get_datapath()))
                client.logger.info(sgr + " has " + str(len(bibliography)) + " references in its bibliography")
                if(DEBUG):
                    print(extended_abs_doc)
                client.logger.info(sgr + " has a doi of " + extended_abs_doc.doi)

                scopus_search = elssearch.ElsSearch(sgr, f"""REF("{extended_abs_doc.title}")""", "scopus")
                scopus_search.execute(els_client=client, get_all=True)
                scopus_id_to_doi_backup = {}
                cited_by = []
                for citing_document in scopus_search.results:
                    if ("dc:identifier" in citing_document):
                        current_scopus_id = citing_document["dc:identifier"].split("SCOPUS_ID:")[1]
                        cited_by.append(current_scopus_id)
                        if ("prism:doi" in citing_document):
                            current_doi = citing_document["prism:doi"]
                            scopus_id_to_doi_backup[current_scopus_id] = current_doi
                if(DEBUG):
                    print(scopus_id_to_doi_backup)

                results_doi_queue.put({
                    "doi": extended_abs_doc.doi,
                    "sgr": extended_abs_doc.int_id,
                    "datapath": extended_abs_doc.get_datapath(),
                    "bibliography": bibliography,
                    "cited_by": cited_by,
                    "scopus_id_to_doi_backup": scopus_id_to_doi_backup,
                })


        except Exception as e:
            client.logger.warning(traceback.format_exc())
            client.logger.warning(e)
            break
    return 0

def run_doi_search(config_file, secrets_file, num_processes):
    cursor_client_dict = get_cursor_client_dict(config_file, secrets_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    client = elsclient.ElsClient(**cursor_client_dict)

    # pool = multiprocessing.Pool(processes=num_processes)
    manager = multiprocessing.Manager()

    api_fetch_size_per_minute = num_processes + 1
    transaction_batch_size = num_processes
    retry = 0
    retry_limit = 3
    timeout_limit = 300 * api_fetch_size_per_minute

    input_doi_queue = manager.Queue()
    results_doi_queue = manager.Queue()

    # pool_result = pool.apply_async(query_api, (cursor_client_dict, input_doi_queue, results_doi_queue, timeout_limit * retry_limit))
    processes = [multiprocessing.Process(target=query_api, args=(cursor_client_dict, input_doi_queue, results_doi_queue, timeout_limit * retry_limit)) for _ in range(num_processes)]
    for current_process in processes:
        current_process.start()


    print(f"starting main while loop")
    while(retry < retry_limit):
        wait_n_minutes(1)
        current_input_queue_size = input_doi_queue.qsize()
        fetch_from_db_size = api_fetch_size_per_minute - current_input_queue_size
        print(f"fetching {fetch_from_db_size}")
        if(fetch_from_db_size > 0):
            cursor.execute(f"SELECT DISTINCT cited FROM europepmc_exosome_citations UNION SELECT DISTINCT citing FROM europepmc_exosome_citations EXCEPT SELECT doi FROM scopus_europepmc_filepaths LIMIT {fetch_from_db_size}")
            rows = cursor.fetchall()
            for row in rows:
                client.logger.info("queueing up " + str(row))
                input_doi_queue.put(row[0])

        timeout = 0
        current_size = results_doi_queue.qsize()
        if(DEBUG):
            print(f"initial check current size: {current_size}")
        while(current_size < transaction_batch_size):
            time.sleep(1)
            if(DEBUG):
                print(f"current size: {current_size}")
            if(timeout > timeout_limit):
                retry += 1
                break
            timeout += 1
            current_size = results_doi_queue.qsize()

        if(timeout < timeout_limit):
            retry = 0
            for i in range(current_size):
                try:
                    current_document = results_doi_queue.get(timeout=1)
                    client.logger.info("added to db transaction: " + str(current_document["doi"]))
                    cursor.execute(f"""INSERT INTO scopus_europepmc_filepaths VALUES ('{current_document['doi']}',{current_document['sgr']}, '{current_document['datapath']}')""")
                    for id_type,cited_id in current_document["bibliography"]:
                        cursor.execute(f"INSERT INTO scopus_europepmc_edgegraph VALUES({current_document['sgr']},{cited_id})")
                    for citing_id in current_document["cited_by"]:
                        cursor.execute(f"INSERT INTO scopus_europepmc_edgegraph VALUES({citing_id},{current_document['sgr']})")
                    for scopus_id,doi in current_document["scopus_id_to_doi_backup"].items():
                        cursor.execute(f"INSERT INTO scopus_europepmc_id_to_doi_backup VALUES({scopus_id},'{doi}') ON CONFLICT (sgr) DO NOTHING")

                except queue.Empty:
                    client.logger.warning(traceback.format_exc())
                    client.logger.warning("Result queue had fewer data than expected, probably due to race conditions.")
                except Exception as e:
                    client.logger.warning(traceback.format_exc())
                    client.logger.warning(e)

            # pull from results_doi_queue into a local varibale
            # INSERT into the new database
            # file_location = client.output_dir + str(doi) + '.json'
            connection.commit()
            time.sleep(10) # giving the db 10 seconds to commit


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
    psql_connection_string = " ".join("{}={}".format(psql_key, psql_connection_dict[psql_key]) for psql_key in psql_connection_dict)
    psql_connection=psycopg2.connect(psql_connection_string)
    cursor = psql_connection.cursor()
    api_key = secrets["apikey"]
    inst_token = secrets["insttoken"]
    output_dir = config["output_dir"]
    log_dir = config["log_dir"]
    return {
        "connection": psql_connection,
        "cursor": cursor,
        "api_key": api_key,
        "inst_token": inst_token,
        "output_dir": output_dir,
        "log_dir": log_dir,
    }

@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the backbonedb and processeddb")
@click.option("--secrets-file", required=True, type=click.Path(exists=True), help="The secrets file containing the api keys")
@click.option("--num-processes", required=False, type=int, default=1, help="Number of Workers")
def doi_search(config_file, secrets_file, num_processes):
    run_doi_search(config_file, secrets_file, num_processes)

if __name__ == "__main__":
    doi_search()
