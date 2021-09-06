import click
import networkx as nx


@click.command()
@click.option("--size", required=True, type=int, help="The size of the complete graph")
@click.option("--output-prefix", required=True, type=click.Path(), help="The output prefix for the complete graph")
def create_complete_graph(size, output_prefix):
    graph = nx.complete_graph(size)
    nx.write_edgelist(graph, output_prefix, delimiter="\t", data=False)


if __name__ == "__main__":
    create_complete_graph()
