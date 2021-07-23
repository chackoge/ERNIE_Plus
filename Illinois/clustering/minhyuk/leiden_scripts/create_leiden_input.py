""" Adapted from https://github.com/ahollocou/modsoft/blob/master/example.ipynb
"""
import click
import networkx as nx


def write_integer_map_and_graph(graph, prefix):
    '''This function takes in an integer mapped graph and writes the mapping
    into a file.
    '''
    graph_labels = {}
    for current_node in graph.nodes():
        graph_labels[current_node] = graph.nodes[current_node]["id"]
    with open(f"{prefix}/nodelabel_to_id.map", "w") as f:
        for current_node in graph_labels:
            f.write(str(current_node) + " " + str(graph.nodes[current_node]["id"]) + "\n")
    nx.write_edgelist(graph, f"{prefix}/citing_cited_network.integer_label.tsv", delimiter="\t", data=False)


@click.command()
@click.option("--network", required=True, type=click.Path(exists=True), help="Input csv edge list")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output mapping and edge list prefix")
@click.option("--delimiter-string", required=False, type=click.Choice(["COMMA", "TAB", "SPACE"]), default="COMMA", help="Delimiter for the input format")
@click.option("--header", required=False, type=bool, default=True, help="Whether there is a header or not")
def create_leiden_input(network, output_prefix, delimiter_string, header):
    '''This is the main function that takes in an edge list in csv format and outputs
    a tsv edge list that is integer encoded
    '''
    original_graph = None
    delimiter = ","
    ''' Not working due to bug?
    if(delimiter == "COMMA"):
        delimiter = ","
    elif(delimiter == "TAB"):
        delimiter = "\t"
    elif(delimiter == "SPACE"):
        delimiter = " "
    '''

    if(header):
        with open(network, "rb") as f:
            next(f, "")
            original_graph = nx.read_edgelist(network, delimiter=delimiter)
    else:
        original_graph = nx.read_edgelist(network, delimiter=delimiter)
    graph = nx.convert_node_labels_to_integers(original_graph, label_attribute="id")
    write_integer_map_and_graph(graph, f"{output_prefix}")


if __name__ == "__main__":
    create_leiden_input()
