""" Adapted from https://github.com/ahollocou/modsoft/blob/master/example.ipynb
"""

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx


def load_leiden_membership_matrix(suffix):
    num_nodes = 0
    num_clusters = -1
    with open(f"./leiden/{suffix}/leiden.clusters", "r") as f:
        for line in f:
            num_nodes += 1
            line_arr = line.split()
            current_row_arr = []
            if(num_clusters < int(line_arr[1])):
                num_clusters = int(line_arr[1])
        num_clusters += 1

    leiden_membership_matrix = np.zeros((num_nodes, num_clusters))
    with open(f"./leiden/{suffix}/leiden.clusters", "r") as f:
        for node_index,line in enumerate(f):
            line_arr = line.split()
            leiden_membership_matrix[node_index,int(line_arr[1])] = 1.0
    return leiden_membership_matrix


def load_louvain_membership_matrix(suffix):
    louvain_membership_matrix = []
    with open(f"./modsoft/{suffix}/louvain_membership_{suffix}.mat", "r") as f:
        for line in f:
            line_arr = line.split()
            current_row_arr = []
            for col in line_arr:
                current_row_arr.append(float(col))
            louvain_membership_matrix.append(current_row_arr)
    return louvain_membership_matrix


def load_modsoft_membership_matrix(suffix):
    modsoft_membership_matrix = []
    with open(f"./modsoft/{suffix}/modsoft_membership_{suffix}.mat", "r") as f:
        for line in f:
            line_arr = line.split()
            current_row_arr = []
            for col in line_arr:
                current_row_arr.append(float(col))
            modsoft_membership_matrix.append(current_row_arr)
    return modsoft_membership_matrix


def plot_communities(graph, suffix, map_file, pos, membership, figure_name, figsize=(10, 10)):
    fig = plt.figure(figsize=figsize)
    ax = plt.axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    color_list = plt.cm.gist_ncar(np.linspace(0, 1, len(membership[0])))
    graph_labels = {}
    with open(f"./{suffix}/nodelabel_to_doi_{suffix}.map", "r") as f:
        for line in f:
            current_line_arr = line.split()
            graph_labels[current_line_arr[0]] = current_line_arr[1]
    nx.draw_networkx(graph, pos, ax=ax, with_labels=True, labels=graph_labels)
    plt.xlim(-0.1, 1.1)
    plt.ylim(-0.1, 1.1)

    global_transform = ax.transData.transform
    local_transform = fig.transFigure.inverted().transform

    pie_size = 0.03
    mid_pie = pie_size / 2.0
    for node in graph:
        x_global,y_global = global_transform(pos[node])
        x_local,y_local = local_transform((x_global, y_global))
        local_ax = plt.axes([x_local - mid_pie, y_local - mid_pie, pie_size, pie_size])
        local_ax.set_aspect("equal")
        fractions = membership[int(node)]
        labels = [str(i) for i in range(len(fractions))]
        for cluster_index in labels:
            if(fractions[int(cluster_index)] < 0.3):
                labels[int(cluster_index)] = ""
        #         labels[cluster_index] = str(cluster_index)
        # labels = [str(i) for i in range(len(membership[int(node)]))]
        # labels = [str(i) for i in range(len(fractions))]
        local_ax.pie(fractions, colors=color_list, labels=labels)
    plt.suptitle(f"{figure_name}")
    plt.savefig(f"./{figure_name}.png")



suffix = "100"

leiden_membership_matrix = load_leiden_membership_matrix(suffix)
# louvain_membership_matrix = load_louvain_membership_matrix(suffix)
# modsoft_membership_matrix = load_modsoft_membership_matrix(suffix)

graph = nx.read_edgelist(f"./{suffix}/kalluri_sample_network.integer_label.{suffix}.tsv")
coordinates = nx.fruchterman_reingold_layout(graph, center=[0.5, 0.5], scale=0.5)

plot_communities(graph, suffix, f"./{suffix}/nodelabel_to_doi_{suffix}.map", coordinates, leiden_membership_matrix, f"{suffix}/leiden_{suffix}")
# plot_communities(graph, suffix, f"./{suffix}/nodelabel_to_doi_{suffix}.map", coordinates, modsoft_membership_matrix, f"{suffix}/modsoft_{suffix}")
# plot_communities(graph, suffix, f"./{suffix}/nodelabel_to_doi_{suffix}.map", coordinates, louvain_membership_matrix, f"{suffix}/louvain_{suffix}")
