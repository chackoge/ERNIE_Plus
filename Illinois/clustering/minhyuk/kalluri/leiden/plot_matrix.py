import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

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

suffix = "100"

num_nodes = 0
num_clusters = -1
with open(f"./{suffix}/leiden.clusters", "r") as f:
    for line in f:
        num_nodes += 1
        line_arr = line.split()
        current_row_arr = []
        if(num_clusters < int(line_arr[1])):
            num_clusters = int(line_arr[1])
    num_clusters += 1

leiden_membership_matrix = np.zeros((num_nodes, num_clusters))
with open(f"./{suffix}/leiden.clusters", "r") as f:
    for node_index,line in enumerate(f):
        line_arr = line.split()
        leiden_membership_matrix[node_index,int(line_arr[1])] = 1.0

graph = nx.read_edgelist(f"./{suffix}/kalluri_sample_network.integer_label.{suffix}.tsv")
coordinates = nx.fruchterman_reingold_layout(graph, center=[0.5, 0.5], scale=0.5)
plot_communities(graph, coordinates, leiden_membership_matrix, f"{suffix}/leiden_{suffix}")
