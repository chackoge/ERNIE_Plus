import click
import numpy as np

from utils import file_to_dict,save_histogram
from sql_utils import get_cursor_client_dict,get_all_doi_and_indegree,get_all_doi_and_outdegree

@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing psql information")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Figure file prefix")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def plot_degree_histogram(config_file, figure_prefix, output_prefix):
    '''This is the main function that takes in a config file with psql table information
    and outputs a histogram of indegree sizes
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    doi_and_indegree_arr = get_all_doi_and_indegree(cursor, table_name)
    doi_and_outdegree_arr = get_all_doi_and_outdegree(cursor, table_name)
    indegrees = [tup[1] for tup in doi_and_indegree_arr]
    outdegrees = [tup[1] for tup in doi_and_outdegree_arr]
    with open(output_prefix + "/report.out", "w") as f:
        f.write(f"Median indegree: {np.median(indegrees)}\n")
        f.write(f"Median outdegree: {np.median(outdegrees)}\n")
        f.write(f"Mean indegree: {np.mean(indegrees)}\n")
        f.write(f"Mean outdegree: {np.mean(outdegrees)}\n")
    with open(output_prefix + "/100_indegree.out", "w") as f_100:
        with open(output_prefix + "/250_indegree.out", "w") as f_250:
            with open(output_prefix + "/500_indegree.out", "w") as f_500:
                for doi,indegree in doi_and_indegree_arr:
                    if(indegree > 500):
                        f_500.write(f"{doi} {indegree}")
                    elif(indegree > 250):
                        f_250.write(f"{doi} {indegree}")
                    elif(indegree > 100):
                        f_100.write(f"{doi} {indegree}")
    save_histogram(0, max(indegrees), 100, indegrees, "Count", "Indegree", "Indegree of exosome 1900 1989", figure_prefix)


if __name__ == "__main__":
    plot_degree_histogram()
