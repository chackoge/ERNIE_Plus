""" Adapted from https://github.com/ahollocou/modsoft/blob/master/example.ipynb
"""
from collections import defaultdict

import community as pylouvain
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

import modsoft



def run_louvain(graph):
    louvain_part = pylouvain.best_partition(graph)
    return louvain_part


def louvain_write_membership_matrix(louvain_partition, suffix)
    louvain_communities = defaultdict(set)
    for node in graph:
        louvain_communities[louvain_partition[node]].add(node)
    louvain_communities = louvain_communities.values()
    louvain_membership_matrix = np.zeros((graph.number_of_nodes(), len(louvain_communities)))
    for k, community in enumerate(louvain_communities):
        for i in community:
            louvain_membership_matrix[i, k] = 1.
    with open(f"./{suffix}/louvain_membership_{suffix}.mat", "w") as f:
        for row in louvain_membership_matrix:
            for col in row:
                f.write(str(col) + " ")
            f.write("\n")
    return louvain_membership_matrix


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


def modsoft_write_membership_matrix(modsoft_membership, suffix):
    modsoft_community_indices = set()
    for membership in modsoft_membership:
        modsoft_community_indices |= set(membership.keys())
    modsoft_community_indices = list(modsoft_community_indices)
    modsoft_community_indices_inv = {index: i for i, index in enumerate(modsoft_community_indices)}
    modsoft_membership_matrix = np.zeros((len(list(graph.nodes())), len(modsoft_community_indices)))
    for i in range(len(list(graph.nodes()))):
        for community in modsoft_membership[i]:
            modsoft_membership_matrix[i][modsoft_community_indices_inv[community]] = modsoft_membership[i][community]

    with open(f"./{suffix}/modsoft_membership_{suffix}.mat", "w") as f:
        for row in modsoft_membership_matrix:
            for col in row:
                f.write(str(col) + " ")
            f.write("\n")
    return modsoft_membership_matrix



def write_integer_map_and_graph(graph, suffix):
    graph_labels = {}
    for current_node in graph.nodes():
        graph_labels[current_node] = graph.nodes[current_node]["doi"]
    with open(f"/home/minhyuk2/git_repos/ERNIE_Plus/Illinois/clustering/minhyuk/kalluri/{suffix}/nodelabel_to_doi_{suffix}.map", "w") as f:
        for current_node in graph_labels:
            f.write(str(current_node) + " " + str(graph.nodes[current_node]["doi"]) + "\n")
    nx.write_edgelist(graph, f"/home/minhyuk2/git_repos/ERNIE_Plus/Illinois/clustering/minhyuk/kalluri/{suffix}/kalluri_sample_network.integer_label.{suffix}.tsv")



suffix = "full"
original_graph = nx.read_edgelist(f"/home/minhyuk2/git_repos/ERNIE_Plus/Illinois/clustering/minhyuk/kalluri/{suffix}/kalluri_sample_network.{suffix}.tsv")
graph = nx.convert_node_labels_to_integers(original_graph, label_attribute="doi")
write_integer_map_and_graph(graph, suffix)

louvain_part  = run_louvain(graph)
modsoft_membersihp = run_modsoft(graph)

louvain_write_membership_matrix(louvain_part, suffix)
modsoft_write_membership_matrix(modsoft_membership, suffix)
