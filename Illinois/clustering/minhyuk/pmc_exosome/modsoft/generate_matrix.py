""" Adapted from https://github.com/ahollocou/modsoft/blob/master/example.ipynb
"""
from collections import defaultdict

import numpy as np
import networkx as nx

import modsoft


def run_modsoft(graph):
    learning_rate=0.7
    max_n_epochs = 15
    epsilon = 1e-4
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

def write_integer_map_and_graph(graph, integer_graph_prefix):
    graph_labels = {}
    for current_node in graph.nodes():
        graph_labels[current_node] = graph.nodes[current_node]["doi"]
    with open(f"{integer_graph_prefix}_nodeid_to_doi.map", "w") as f:
        for current_node in graph_labels:
            f.write(str(current_node) + " " + str(graph.nodes[current_node]["doi"]) + "\n")
    nx.write_edgelist(graph, f"{integer_graph_prefix}_integer_graph.tsv")



original_graph_path = "/srv/local/shared/external/mcl_analysis/europepmc_exosome_analysis/europepmc_exosome_edgelist.tsv"
integer_graph_prefix = "./integer_graph.tsv"
modsoft_output = "./modsoft.clusters"
original_graph = nx.read_edgelist(original_graph_path)
graph = nx.convert_node_labels_to_integers(original_graph, label_attribute="doi")
write_integer_map_and_graph(graph, integer_graph_prefix)

print("starting modsoft")
modsoft_membership = run_modsoft(graph)
with open(f"{modsoft_output}", "w") as f:
    for row in modsoft_membership:
        f.write(f"{row}\n")
