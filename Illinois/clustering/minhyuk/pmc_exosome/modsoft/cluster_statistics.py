import json

import click
import matplotlib.pyplot as plt
import numpy as np

@click.command()
@click.option("--input-clusters", required=True, type=click.Path(exists=True), help="Clustering output")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output histogram prefix")
def cluster_statistics(input_clusters, output_prefix):
    cluster_dict = {}
    with open(input_clusters, "r") as f:
        for line in f:
            line_arr = line.split()
            current_node_num = line_arr[0]
            current_cluster_membership = line_arr[1:]
            for membership in current_cluster_membership:
                if(membership not in cluster_dict):
                    cluster_dict[membership] = []
                cluster_dict[membership].append(current_node_num)

    singleton_arr = []
    cluster_size_data = []
    cluster_data = []
    for cluster,cluster_members in cluster_dict.items():
        if(len(cluster_members) == 1):
            singleton_arr.append(cluster_members[0])
        cluster_size_data.append(len(cluster_members))
        cluster_data.extend([cluster] * len(cluster_members))
    num_clusters = len(cluster_dict)
    print(num_clusters)
    return

    if(len(singleton_arr) > 0):
        with open(output_prefix + "singletons.node", "w") as f:
            for singleton_node in singleton_arr:
                f.write(str(singleton_node) + "\n")
    bins = np.arange(0, 11, 1)
    plt.hist(cluster_size_data, bins=bins, density=False)
    plt.ylabel("Cluster Count")
    plt.xlabel("Cluster Sizes");
    plt.title(output_prefix);
    plt.savefig(output_prefix + "_cluster_sizes.png", bbox_inches='tight')

if __name__ == "__main__":
    cluster_statistics()
