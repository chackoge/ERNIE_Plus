import json

import click
import matplotlib.pyplot as plt
import networkit as nk
import numpy as np

@click.command()
@click.option("--input-clusters", required=True, type=click.Path(exists=True), help="Clustering output")
@click.option("--input-network", required=True, type=click.Path(exists=True), help="Input network")
@click.option("--figure-prefix", required=True, type=click.Path(), help="Output histogram prefix")
def cluster_size_histogram_networkit(input_clusters, input_network, figure_prefix):
    '''This is the main function that takes in an input clustering output in the format
    where line i has "<cluster number>" for node i. Input network should be an edge list
    with node ids corresponding to the input network where all the node ids are integers
    '''
    graph = nk.readGraph(input_network, nk.Format.EdgeListTabZero)
    partition = nk.community.readCommunities(input_clusters)
    sizes = partition.subsetSizes()
    # sizes.sort(reverse=True)
    ax = plt.subplot(1, 1, 1)
    ax.set_ylabel("size")
    ax.plot(sizes)
    ax.ticklabel_format(style="plain")
    plt.savefig(f"{figure_prefix}_cluster_number_to_size_plot.png")
    # this will print a tabluar format like
    '''
    -------------------  -------------
    # communities          number
    min community size     number
    max community size     number
    avg. community size    number
    modularity             number
    -------------------  -------------
    '''
    nk.community.inspectCommunities(partition, graph)


if __name__ == "__main__":
    cluster_size_histogram_networkit()
