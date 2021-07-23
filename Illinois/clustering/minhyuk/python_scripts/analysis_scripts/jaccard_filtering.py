import json
import multiprocessing
import queue

import click
import matplotlib.pyplot as plt
import numpy as np


def file_to_dict(clustering):
    cluster_dict = {}
    with open(clustering, "r") as f:
        for current_line in f:
            [current_cluster_number, doi] = current_line.strip().split()
            if(current_cluster_number not in cluster_dict):
                cluster_dict[current_cluster_number] = []
            cluster_dict[current_cluster_number].append(doi)
    return cluster_dict


def get_jaccard_score(clustering_base_arr, clustering_support_arr):
    current_jaccard_score = None
    base_set = set(clustering_base_arr)
    support_set = set(clustering_support_arr)
    jaccard_intersection = base_set.intersection(support_set)
    jaccard_union = base_set.union(support_set)
    current_jaccard_score = len(jaccard_intersection) / len(jaccard_union)
    return current_jaccard_score


def get_maximum_jaccard_score_wrapper(args):
    return get_maximum_jaccard_score(*args)

def get_maximum_jaccard_score(base_cluster_counter, base_cluster_number, base_cluster_arr, support_cluster_dict):
    if(base_cluster_counter % 1000 == 0):
        print(f"started cluster_counter count: {base_cluster_counter}")
    current_max_jaccard_score = 0
    current_base_cluster_size = len(base_cluster_arr)
    for support_cluster_number,current_support_cluster_arr in support_cluster_dict.items():
        max_overlap_jaccard_score = len(current_support_cluster_arr) / len(base_cluster_arr)
        if(max_overlap_jaccard_score > current_max_jaccard_score):
            # there's a chance that this cluster could beat the previous best score
            current_max_jaccard_score = max(current_max_jaccard_score, get_jaccard_score(base_cluster_arr, current_support_cluster_arr))
    if(base_cluster_counter % 1000 == 0):
        print(f"{base_cluster_counter}")
        print(f"finished {base_cluster_counter} clusters so far")
    return (base_cluster_number,current_max_jaccard_score)

@click.command()
@click.option("--base-clustering", required=True, type=click.Path(exists=True), help="Clustering output to be used as base clusters")
@click.option("--support-clustering", required=True, type=click.Path(), help="Clustering output to be used as support clusters")
@click.option("--num-processes", required=True, type=int, help="Number of processes")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def jaccard_filtering(base_clustering, support_clustering, num_processes, output_prefix):
    print(f"Starting execution for {output_prefix}")
    base_cluster_dict = file_to_dict(base_clustering)
    print(f"Base cluster dict generated")
    support_cluster_dict = file_to_dict(support_clustering)
    print(f"Support cluster dict generated")


    jaccard_score_args_arr = []
    base_cluster_counter = 0
    for base_cluster_number,current_base_cluster_arr in base_cluster_dict.items():
        jaccard_score_args_arr.append((base_cluster_counter, base_cluster_number, base_cluster_dict[base_cluster_number], support_cluster_dict))
        base_cluster_counter += 1

    print(f"Started Pool")
    pool = multiprocessing.Pool(processes=num_processes)
    cluster_jaccard_score_tuple_arr = pool.map(get_maximum_jaccard_score_wrapper, jaccard_score_args_arr)
    print(f"Finished Pool")

    # manager = multiprocessing.Manager()
    # input_queue = manager.Queue()
    # result_queue = manager.Queue()

    # # pool_result = pool.apply_async(query_api, (cursor_client_dict, input_doi_queue, results_doi_queue, timeout_limit * retry_limit))
    # processes = [multiprocessing.Process(target=query_api, args=(input_queue, result_queue) for _ in range(num_processes)]
    # for current_process in processes:
    #     current_process.start()

    # for current_process in processes:
    #     current_process.start()


    jaccard_score_data = []
    cluster_size_data = []
    with open(output_prefix + "clusternum_jaccardscore.data", "w") as f:
        for base_cluster_number,jaccard_score in cluster_jaccard_score_tuple_arr:
            f.write(str(base_cluster_number) + " " + str(jaccard_score) + "\n")
            jaccard_score_data.append(jaccard_score)
            cluster_size_data.append(len(base_cluster_dict[base_cluster_number]))

    bins = np.arange(0, 1.01, 0.01)
    plt.hist(jaccard_score_data, bins=bins, density=False)
    plt.ylabel("Count")
    plt.xlabel("Jaccard Score (1 = maximum overlap, 0 = no overlap)");
    plt.title(output_prefix);
    plt.savefig(output_prefix + "_jaccard_scores_histogram.png", bbox_inches="tight")

    plt.figure()

    plt.scatter(cluster_size_data, jaccard_score_data)
    plt.xlabel("Cluster Sizes")
    plt.ylabel("Jaccard Scores")
    plt.title(output_prefix)
    plt.savefig(output_prefix + "_jaccard_score_cluster_size_scatter.png", bbox_inches="tight")

    print(f"Finished execution for {output_prefix}")


if __name__ == "__main__":
    jaccard_filtering()
