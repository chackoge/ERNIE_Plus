from collections import defaultdict

import community as pylouvain
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

import modsoft

# def plot_communities(graph, pos, membership, figure_name, figsize=(10, 10)):

#     fig = plt.figure(figsize=figsize)
#     ax = plt.axes([0, 0, 1, 1])
#     ax.set_aspect('equal')
#     # nx.draw_networkx(graph, pos, ax=ax, with_labels=True, labels=graph_labels)
#     nx.draw_networkx_edges(graph, pos, ax=ax)
#     plt.xlim(-0.1, 1.1)
#     plt.ylim(-0.1, 1.1)

#     trans = ax.transData.transform
#     trans2 = fig.transFigure.inverted().transform

#     pie_size = 0.05
#     p2 = pie_size / 2.0
#     for node in graph:
#         xx, yy = trans(pos[node])   # figure coordinates
#         xa, ya = trans2((xx, yy))   # axes coordinates
#         a = plt.axes([xa - p2, ya - p2, pie_size, pie_size])
#         a.set_aspect('equal')
#         fractions = membership[int(node)]
#         a.pie(fractions)
#     plt.savefig(f"./{figure_name}.png")

def plot_communities(graph, pos, membership, figure_name, figsize=(10, 10)):

    fig = plt.figure(figsize=figsize)
    ax = plt.axes([0, 0, 1, 1])
    ax.set_aspect('equal')

    color_list = plt.cm.gist_ncar(np.linspace(0, 1, len(membership[0])))
    # a.set_prop_cycle("color", color_list)

    # nx.draw_networkx(graph, pos, ax=ax, with_labels=True, labels=graph_labels)
    nx.draw_networkx_edges(graph, pos, ax=ax)
    plt.xlim(-0.1, 1.1)
    plt.ylim(-0.1, 1.1)

    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform

    pie_size = 0.03
    p2 = pie_size / 2.0
    for node in graph:
        xx, yy = trans(pos[node])   # figure coordinates
        xa, ya = trans2((xx, yy))   # axes coordinates
        a = plt.axes([xa - p2, ya - p2, pie_size, pie_size])
        a.set_aspect("equal")
        fractions = membership[int(node)]
        labels = [str(i) for i in range(len(fractions))]
        # labels = ["" * len(fractions)]
        for cluster_index in labels:
            if(fractions[int(cluster_index)] < 0.3):
                labels[int(cluster_index)] = ""
        #         labels[cluster_index] = str(cluster_index)
        # labels = [str(i) for i in range(len(membership[int(node)]))]
        # labels = [str(i) for i in range(len(fractions))]
        a.pie(fractions, colors=color_list, labels=labels)
    plt.suptitle(f"{figure_name}")
    plt.savefig(f"./{figure_name}.png")

suffix = "1000"
graph = nx.read_edgelist(f"./{suffix}/kalluri_sample_network.integer_label.{suffix}.tsv")
coordinates = nx.fruchterman_reingold_layout(graph, center=[0.5, 0.5], scale=0.5)


louvain_membership_matrix = []
modsoft_membership_matrix = []

with open(f"./{suffix}/louvain_membership_{suffix}.mat", "r") as f:
    for line in f:
        line_arr = line.split()
        current_row_arr = []
        for col in line_arr:
            current_row_arr.append(float(col))
        louvain_membership_matrix.append(current_row_arr)

with open(f"./{suffix}/modsoft_membership_{suffix}.mat", "r") as f:
    for line in f:
        line_arr = line.split()
        current_row_arr = []
        for col in line_arr:
            current_row_arr.append(float(col))
        modsoft_membership_matrix.append(current_row_arr)

plot_communities(graph, coordinates, modsoft_membership_matrix, f"{suffix}/modsoft_{suffix}")
plot_communities(graph, coordinates, louvain_membership_matrix, f"{suffix}/louvain_{suffix}")
