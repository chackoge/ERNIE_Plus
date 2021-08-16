import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict,run_mcl,run_leiden,write_new_sorted_cluster_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_num_edges,get_sum_num_degrees,get_intracluster_num_edges,get_intracluster_num_degree


def get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, k, t, b):
   ''' equation 2 is defined by \frac{l_{s}}{L} - (\frac{d_{s}}{2L})^{2} > t where t is zero
   where l_s is the number of edges in cluster s, L is the number of edges in the
   entire network, and d_s is the total sum of the degrees of each node inside cluster s
   When this value is greater than t, it is considered a valid module in terms of modularity
   criterion. Each cluster must also be of size at least B.
   '''
   cluster_size_valid = True
   if(len(cluster_member_arr) < b):
       cluster_size_valid = False

   node_degree_valid = True
   intracluster_node_degree_arr = get_intracluster_num_degree(cursor, table_name, cluster_member_arr)
   for node,degree in intracluster_node_degree_arr:
       if(degree < k):
           node_degree_valid = False

   L = get_num_edges(cursor, table_name)
   l_s = get_intracluster_num_edges(cursor, table_name, cluster_member_arr)
   d_s = get_sum_num_degrees(cursor, table_name, cluster_member_arr)
   equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
   # print(f"-- -- for cluster {cluster_member_arr}, b={len(cluster_member_arr)}, k arr={intracluster_node_degree_arr}, L={L}, l_s={l_s}, d_s={d_s}, and equation 2 = {equation_2}")
   return {
       "is_valid": equation_2 >= t and cluster_size_valid and node_degree_valid,
       "equation_2": equation_2,
       "k_arr": [int(tup[1]) for tup in intracluster_node_degree_arr],
   }


def run_leiden_on_cluster(graph, cluster_to_id_dict, cluster_id_to_split, resolution_value, output_prefix):
    ''' This runs leiden on a cluster specified by the cluster_id_to_split
    and updates the cluster_to_id_dict by creating new clusters with cluster id
    starting from the current max cluster_id  + 1.
    Note that it does not erase the original cluster
    '''
    new_cluster_ids = []
    subgraph = nk.graphtools.subgraphFromNodes(graph, [int(integer_node_id) for integer_node_id in cluster_to_id_dict[cluster_id_to_split]])
    new_node_map = nk.graphtools.getContinuousNodeIds(subgraph)
    compacted_graph = nk.graphtools.getCompactedGraph(subgraph, new_node_map)
    compacted_graph_filename = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}.tsv"
    leiden_output_prefix = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}"
    nk.writeGraph(compacted_graph, compacted_graph_filename, nk.Format.EdgeListTabZero)
    compacted_graph_clusters = run_leiden(compacted_graph_filename, resolution_value, leiden_output_prefix)
    inverse_node_map = {new_id: old_id for old_id,new_id in new_node_map.items()}
    new_cluster_index = max(cluster_to_id_dict.keys()) + 1
    for cluster,cluster_members in compacted_graph_clusters.items():
        cluster_to_id_dict[new_cluster_index] = []
        for new_cluster_member_id in cluster_members:
            cluster_to_id_dict[new_cluster_index].append(str(inverse_node_map[int(new_cluster_member_id)]))
        new_cluster_ids.append(new_cluster_index)
        new_cluster_index += 1
    return new_cluster_ids


@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the postgres connection details")
@click.option("--network", required=True, type=click.Path(exists=True), help="Integer labelled edgelist")
@click.option("--resolution-value", required=True, type=float, help="Resolution value for Leiden")
@click.option("--k", required=True, type=int, help="The minimum connectivity among each other in a cluster to be considered valid")
@click.option("--t", required=True, type=float, help="The minimum modularity threshold for each cluster")
@click.option("--b", required=True, type=int, help="The minimum modularity threshold for each cluster")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def recursive_leiden(config_file, network, resolution_value, k, t, b, output_prefix):
    '''This is the main function that will take in a tsv integer labelled network and recursively
    run leiden on the network and its clusters until we can no longer split a cluster into its
    valid constituents where valid is defined by a positive modularity score
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    graph = nk.readGraph(network, nk.Format.EdgeListTabZero)
    initial_leiden_filename = f"{output_prefix}/initial_graph"
    cluster_to_id_dict = run_leiden(network, resolution_value, initial_leiden_filename)
    cluster_id_stack = list(cluster_to_id_dict.keys())
    with open(f"{output_prefix}/recursive_leiden.log", "w") as f:
        f.write(f"// After running leiden initially, we start with {len(cluster_id_stack)} clusters\n")
        f.write(f"// the -42 magic number indicates that the cluster has zero intracluster connections\n")
        f.write(f"// this usually means that the current cluster is singleton\n")

    iteration_number = 0 # this is purely for logging purposes
    logging_dict = {}
    while(len(cluster_id_stack) > 0):
        # print(f"A new iteration!")
        current_cluster_id = cluster_id_stack.pop()
        cluster_member_arr = cluster_to_id_dict[current_cluster_id]
        # array for logging and tracing purposes
        decomposed_into = []
        # print(f"-- In this iteration, we are inspecting cluster {current_cluster_id} with members {cluster_member_arr}")
        cluster_info_dict = get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, k, t, b)
        if(cluster_info_dict["is_valid"]):
            # print(f"-- cluster {current_cluster_id} with members {cluster_member_arr} is a valid cluster")
            new_cluster_ids = run_leiden_on_cluster(graph, cluster_to_id_dict, current_cluster_id, resolution_value, output_prefix)
            # extending instead of pushing every element
            at_least_one_subcluster_valid = False
            for new_cluster_id in new_cluster_ids:
                decomposed_into.append(new_cluster_id)
                at_least_one_subcluster_valid |= get_cluster_info_dict(cursor, table_name, graph, cluster_to_id_dict[new_cluster_id], k, t, b)["is_valid"]
            if(at_least_one_subcluster_valid and len(new_cluster_ids) > 1):
                # print(f"-- cluster {current_cluster_id} with members {cluster_member_arr} has been split into {len(new_cluster_ids)}, which will be validated later")
                cluster_id_stack.extend(new_cluster_ids)
                # the current cluster has successfully decomposed into at least one valid cluster
                cluster_to_id_dict[current_cluster_id] = []
            else:
                # either the current cluster fully dissolved and we keep this cluster as it cannot go any smaller
                # or leiden returned only one cluster which is itself so we keep this cluster
                # invalidate any new cluster returend by our algorithm
                '''
                if(not at_least_one_subcluster_valid):
                    print(f"-- Cannot split cluster {current_cluster_id} consisting of {cluster_member_arr} since none of its subclusters returned by leiden is valid")
                if(len(new_cluster_ids) == 1):
                    print(f"-- Cannot split cluster {current_cluster_id} consisting of {cluster_member_arr} since leiden could not split this cluster into multiple clusters")
                '''
                for new_cluster_id in new_cluster_ids:
                    cluster_to_id_dict.pop(new_cluster_id)
        else:
            # print(f"cluster {current_cluster_id} consisting of {cluster_member_arr} is not valid")
            pass

        # code for logging
        if(len(cluster_info_dict["k_arr"]) == 0):
            # this -42 magic number indicates that the cluster has zero intracluster connections
            # this usually means that the current cluster is a singleton
            cluster_info_dict["k_arr"] = [-42]

        logging_dict[current_cluster_id] = {
            "is_valid": cluster_info_dict["is_valid"],
            "modularity": cluster_info_dict["equation_2"],
            "connectivity": {
                "min_k": np.min(cluster_info_dict["k_arr"]),
                "max_k": np.max(cluster_info_dict["k_arr"]),
                "median_k": np.median(cluster_info_dict["k_arr"]),
                "mean_k": np.mean(cluster_info_dict["k_arr"]),
                "percentile_k": {
                    "10": np.percentile(cluster_info_dict["k_arr"], 10),
                    "25": np.percentile(cluster_info_dict["k_arr"], 25),
                    "75": np.percentile(cluster_info_dict["k_arr"], 75),
                    "90": np.percentile(cluster_info_dict["k_arr"], 90),
                },
            },
            "decomposed_into": decomposed_into,
            "iteration_number": iteration_number,
        }
    with open(f"{output_prefix}/recursive_leiden.log", "a") as f:
        f.write(f"cluster_id,is_valid,modularity,min_k,max_k,median_k,mean_k,10th_percentile,25th_percentile,75th_percentile,90th_percentile,decomposed_into,iteration_number\n")
        for current_cluster_id in logging_dict:
            f.write(f"{current_cluster_id},")
            f.write(f"{logging_dict[current_cluster_id]['is_valid']},")
            f.write(f"{logging_dict[current_cluster_id]['modularity']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['min_k']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['max_k']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['median_k']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['mean_k']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['percentile_k']['10']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['percentile_k']['25']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['percentile_k']['75']},")
            f.write(f"{logging_dict[current_cluster_id]['connectivity']['percentile_k']['90']},")
            f.write(f"{logging_dict[current_cluster_id]['decomposed_into']},")
            f.write(f"{logging_dict[current_cluster_id]['iteration_number']}")
            f.write(f"\n")

    write_new_sorted_cluster_dict(cluster_to_id_dict, [], f"{output_prefix}/recursive_leiden_k_{k}_t_{t}_b_{b}")

if __name__ == "__main__":
    recursive_leiden()
