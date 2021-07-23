import click
import numpy as np

from python_scripts.utils.utils import file_to_dict,save_histogram
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_all_id_and_indegree,get_all_id_and_outdegree

@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing psql information")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Figure file prefix")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def get_network_degree_info(config_file, figure_prefix, output_prefix):
    '''This is the main function that takes in a config file with psql table information
    and outputs a set of files containing the degree information
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    id_and_indegree_arr = get_all_id_and_indegree(cursor, table_name)
    id_and_outdegree_arr = get_all_id_and_outdegree(cursor, table_name)
    indegrees = [tup[1] for tup in id_and_indegree_arr]
    outdegrees = [tup[1] for tup in id_and_outdegree_arr]
    with open(output_prefix + "/report.out", "w") as f:
        f.write(f"Median indegree: {np.median(indegrees)}\n")
        f.write(f"Median outdegree: {np.median(outdegrees)}\n")
        f.write(f"Mean indegree: {np.mean(indegrees)}\n")
        f.write(f"Mean outdegree: {np.mean(outdegrees)}\n")
        f.write(f"Max indegree: {np.max(indegrees)}\n")
        f.write(f"Max outdegree: {np.max(outdegrees)}\n")
        f.write(f"Min indegree: {np.min(indegrees)}\n")
        f.write(f"Min outdegree: {np.min(outdegrees)}\n")
    with open(output_prefix + "/raw.data", "w") as f:
        for dimensions_id,indegree in id_and_indegree_arr:
            f.write(f"{dimensions_id} {indegree}\n")
    #save_histogram(0, np.max(indegrees), 100, indegrees, "Count", "Indegree", "Indegree of exosome 1900 1989", figure_prefix + "/network_indegree_histogram_MANUALRETURN")
    with open(output_prefix + "/100_indegree.out", "w") as f_100:
        with open(output_prefix + "/250_indegree.out", "w") as f_250:
            with open(output_prefix + "/500_indegree.out", "w") as f_500:
                for dimensions_id,indegree in id_and_indegree_arr:
                    if(indegree > 500):
                        f_500.write(f"{dimensions_id} {indegree}\n")
                    if(indegree > 250):
                        f_250.write(f"{dimensions_id} {indegree}\n")
                    if(indegree > 100):
                        f_100.write(f"{dimensions_id} {indegree}\n")


if __name__ == "__main__":
    get_network_degree_info()
