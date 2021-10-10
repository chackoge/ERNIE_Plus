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
                [current_cluster_number, current_id] = current_line.strip().split(",")
                fw.write(current_cluster_number + " " + current_id + "\n")


def parse_ikc(clustering_output, output_prefix):
    '''This function takes in the raw ikc cluster format which is
    node Id, cluster nbr, and value of k for which cluster nbr was generated (and modularity)
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    with open(output_prefix, "w") as fw:
        with open(clustering_output, "r") as f:
            for line_number,current_line in enumerate(f):
                [node_id, cluster_number, k, modularity] = current_line.strip().split(",")
                fw.write(cluster_number + " " + node_id + "\n")


def parse_graclus(clustering_output, output_prefix):
    '''This function takes in the raw graclus cluster format which is
    line i contains cluster number for node i
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    id_to_cluster_dict = {}
    with open(clustering_output, "r") as f:
        for line_number,current_line in enumerate(f):
            id_to_cluster_dict[line_number] = current_line.strip()
    with open(output_prefix, "w") as fw:
        for cluster_id,cluster_number in id_to_cluster_dict.items():
            fw.write(f"{cluster_number} {cluster_id}\n")


def parse_leiden(clustering_output, leiden_mapping, output_prefix):
    ''' This function takes in the leiden cluster format and optionally a leiden integer mapping
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    integer_to_id_mapping = {}
    input_file = None
    if(leiden_mapping is not None):
        input_file = leiden_mapping
        with open(input_file, "r") as f:
            for current_line in f:
                [integer_label, node_id] = current_line.split()
                integer_to_id_mapping[integer_label] = node_id

        with open(output_prefix, "w") as fw:
            with open(clustering_output, "r") as f:
                for current_line in f:
                    [integer_label, current_cluster_number] = current_line.strip().split()
                    fw.write(current_cluster_number + " " + integer_to_id_mapping[integer_label] + "\n")
    else:
        input_file = clustering_output
        with open(output_prefix, "w") as fw:
            with open(clustering_output, "r") as f:
                for current_line in f:
                    [integer_label, current_cluster_number] = current_line.strip().split()
                    fw.write(current_cluster_number + " " + integer_label + "\n")


@click.command()
@click.option("--clustering-output", required=True, type=click.Path(exists=True), help="Clustering output to be converted")
@click.option("--leiden-mapping", required=False, type=click.Path(exists=True), help="Leiden integer mapping")
@click.option("--cluster-method", required=True, type=click.Choice(["mcl", "leiden", "ikc", "graclus"]), help="Clustering method used")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def convert_to_cluster_id_format(clustering_output, leiden_mapping, cluster_method, output_prefix):
    '''This is the main function that takes in either mcl or leiden formatted clustering output
    and writes a cluster format where each line is "<cluster number>SPACE<node id>"
    '''
    if(cluster_method == "mcl"):
        parse_mcl(clustering_output, output_prefix)
    elif(cluster_method == "leiden"):
        parse_leiden(clustering_output, leiden_mapping, output_prefix)
    elif(cluster_method == "ikc"):
        parse_ikc(clustering_output, output_prefix)
    elif(cluster_method == "graclus"):
        parse_graclus(clustering_output, output_prefix)


if __name__ == "__main__":
    convert_to_cluster_id_format()
