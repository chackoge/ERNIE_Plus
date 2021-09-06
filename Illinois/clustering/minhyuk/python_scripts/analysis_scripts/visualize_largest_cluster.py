import time

import click
import matplotlib.pyplot as plt
import networkx as nx

from python_scripts.utils.utils import file_to_dict


@click.command()
@click.option("--network", required=True, type=click.Path(exists=True), help="The tsv edgelist representing a network")
@click.option("--input-clusters", required=True, type=click.Path(exists=True), help="The clustering file")
@click.option("--figure-prefix", required=True, type=click.Path(), help="The prefix for figure output")
def visualize_largest_cluster(network, input_clusters, figure_prefix):
    '''This script assumes that cluster 0 is the largest cluster
    and visualizes it using networkx
    '''
    graph = nx.read_edgelist(network, delimiter="\t", data=False)
    cluster_dicts = file_to_dict(input_clusters)
    cluster_to_id_dict = cluster_dicts["cluster_to_id_dict"]
    id_to_cluster_dict = cluster_dicts["id_to_cluster_dict"]
    largest_cluster_nodes = cluster_to_id_dict[0]
    subgraph = graph.subgraph(largest_cluster_nodes)
    nx.draw(subgraph, with_labels=True, font_weight="bold")
    plt.savefig(f"{figure_prefix}.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    visualize_largest_cluster()
