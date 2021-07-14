""" Adapted from https://github.com/ahollocou/modsoft/blob/master/example.ipynb
"""
from collections import defaultdict

import click
import community as pylouvain
import matplotlib.pyplot as plt
import modsoft
import numpy as np
import networkx as nx


def run_louvain(graph):
    '''This function runs louvain clustering and returns the output clustering
    '''
    louvain_part = pylouvain.best_partition(graph)
    return louvain_part


def louvain_write_membership_matrix(louvain_partition, prefix)
    '''This function writes the louvain membership matrix where the rows are nodes and
    the columns are the clusters. The cell[i,j] is 1 if the node i belongs in cluster j
    '''
    louvain_communities = defaultdict(set)
    for node in graph:
        louvain_communities[louvain_partition[node]].add(node)
    louvain_communities = louvain_communities.values()
    louvain_membership_matrix = np.zeros((graph.number_of_nodes(), len(louvain_communities)))
    for k, community in enumerate(louvain_communities):
        for i in community:
            louvain_membership_matrix[i, k] = 1.
    with open(f"{prefix}/louvain_membership.mat", "w") as f:
        for row in louvain_membership_matrix:
            for col in row:
                f.write(str(col) + " ")
            f.write("\n")
    return louvain_membership_matrix


def run_modsoft(graph, learning_rate, max_n_epochs, epsilon):
    '''This function runs modsoft and returns the output membership matrix
    '''
    ms = modsoft.get_modsoft_object(graph, learning_rate=learning_rate)
    modsoft_mod = ms.modularity()
    for i in range(max_n_epochs):
        ms.one_step()
        new_modsoft_mod = ms.modularity()
        if abs(new_modsoft_mod - modsoft_mod) < epsilon:
            break
        else:
            modsoft_mod = new_modsoft_mod
    modsoft_membership = ms.get_membership()
    return modsoft_membership


def modsoft_write_membership_matrix(modsoft_membership, prefix):
    '''This function writes the modsoft membership matrix where the rows
    are nodes and the columns are the clusters. The cell[i,j] is p if node i
    has probability p of belonging in cluster j.
    '''
    modsoft_community_indices = set()
    for membership in modsoft_membership:
        modsoft_community_indices |= set(membership.keys())
    modsoft_community_indices = list(modsoft_community_indices)
    modsoft_community_indices_inv = {index: i for i, index in enumerate(modsoft_community_indices)}
    modsoft_membership_matrix = np.zeros((len(list(graph.nodes())), len(modsoft_community_indices)))
    for i in range(len(list(graph.nodes()))):
        for community in modsoft_membership[i]:
            modsoft_membership_matrix[i][modsoft_community_indices_inv[community]] = modsoft_membership[i][community]

    with open(f"./{prefix}/modsoft_membership.mat", "w") as f:
        for row in modsoft_membership_matrix:
            for col in row:
                f.write(str(col) + " ")
            f.write("\n")
    return modsoft_membership_matrix


def write_integer_map_and_graph(graph, prefix):
    '''This function takes in an integer mapped graph and writes the mapping
    into a file.
    '''
    graph_labels = {}
    for current_node in graph.nodes():
        graph_labels[current_node] = graph.nodes[current_node]["doi"]
    with open(f"{prefix}/nodelabel_to_doi.map", "w") as f:
        for current_node in graph_labels:
            f.write(str(current_node) + " " + str(graph.nodes[current_node]["doi"]) + "\n")
    nx.write_edgelist(graph, f"{prefix}.integer_label.tsv")


@click.command()
@click.option("--network", required=True, type=click.Path(exists=True), help="Input tsv edge list")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output cluster file prefix")
@click.option("--learning-rate", required=False, type=float, default=0.7, help="Learning rate for modsoft")
@click.option("--num-epochs", required=False, type=int, default=15, help="Maximum number of epochs for modsoft")
@click.option("--epsilon", required=False, type=float, default=0.0001, help="Epsilon for modsoft")
def generate_matrix(network, output_prefix, learning_rate, num_epochs, epsilon):
    '''This is the main function that takes in an edge list and runs louvain and modsoft
    '''
    original_graph = nx.read_edgelist(network)
    graph = nx.convert_node_labels_to_integers(original_graph, label_attribute="doi")
    write_integer_map_and_graph(graph, f"{output_prefix}")

    louvain_part  = run_louvain(graph)
    modsoft_membersihp = run_modsoft(graph, learning_rate, num_epochs, epsilon)

    louvain_write_membership_matrix(louvain_part, output_prefix)
    modsoft_write_membership_matrix(modsoft_membership, output_prefix)


if __name__ == "__main__":
    generate_matrix()
