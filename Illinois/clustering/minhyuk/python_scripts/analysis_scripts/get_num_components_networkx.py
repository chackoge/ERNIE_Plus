import time

import click
import networkx as nx


@click.command()
@click.option("--network", required=True, type=click.Path(exists=True), help="The csv edgelist representing a network")
def get_num_components_networkx(network):
    graph = nx.read_edgelist(network, delimiter="\t", data=False)
    for component_index,connected_component in enumerate(nx.connected_components(graph)):
        print(f"component {component_index} has size {len(connected_component)}")


if __name__ == "__main__":
    get_num_components_networkx()
