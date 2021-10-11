import click


@click.command()
@click.option("--input-clustering", required=True, type=click.Path(exists=True), help="Clustering to be converted")
@click.option("--output-clustering", required=True, type=click.Path(), help="Clustering output")
def convert_to_cluster_comma_node(input_clustering, output_clustering):
    '''This is the main function that takes in a clustering of format
    "<cluster_id>SPACE<node_id>" and writes a cluster format where
    each line is "<cluster number>,<node id>"
    '''
    with open(output_clustering, "w") as fw:
        with open(input_clustering, "r") as f:
            for line_number,current_line in enumerate(f):
                [cluster_id, node_id] = current_line.strip().split(" ")
                fw.write(cluster_id + "," + node_id + "\n")


if __name__ == "__main__":
    convert_to_cluster_comma_node()
