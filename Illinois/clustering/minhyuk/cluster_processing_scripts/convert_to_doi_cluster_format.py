import json

import click


def parse_mcl(clustering_output, output_prefix):
    ''' This function takes in the mcl output cluster format
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    with open(output_prefix, "w") as fw:
        with open(clustering_output, "r") as f:
            for line_number,current_line in enumerate(f):
                if(line_number == 0):
                    continue
                [current_cluster_number, current_doi] = current_line.strip().split(",")
                fw.write(current_cluster_number + " " + current_doi + "\n")

def parse_leiden(clustering_output, leiden_mapping, output_prefix):
    ''' This function takes in the leiden cluster format and leiden integer mapping
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    integer_to_doi_mapping = {}
    with open(leiden_mapping, "r") as f:
        for current_line in f:
            [integer_label, doi] = current_line.split()
            integer_to_doi_mapping[integer_label] = doi

    with open(output_prefix, "w") as fw:
        with open(clustering_output, "r") as f:
            for current_line in f:
                [integer_label, current_cluster_number] = current_line.strip().split()
                fw.write(current_cluster_number + " " + integer_to_doi_mapping[integer_label] + "\n")

@click.command()
@click.option("--clustering-output", required=True, type=click.Path(exists=True), help="Clustering output to be converted")
@click.option("--leiden-mapping", required=False, type=click.Path(exists=True), help="Leiden integer mapping")
@click.option("--cluster-method", required=True, type=click.Choice(["mcl", "leiden"]), help="Clustering method used")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def convert_to_doi_cluster_format(clustering_output, leiden_mapping, cluster_method, output_prefix):
    '''This is the main function that takes in either mcl or leiden formatted clustering output
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    if(cluster_method == "mcl"):
        parse_mcl(clustering_output, output_prefix)
    if(cluster_method == "leiden"):
        parse_leiden(clustering_output, leiden_mapping, output_prefix)

if __name__ == "__main__":
    convert_to_doi_cluster_format()
