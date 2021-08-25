import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict,run_mcl,run_leiden,write_new_sorted_cluster_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_num_edges,get_sum_num_degrees,get_intracluster_num_edges,get_intracluster_num_degree



def get_best_leiden(cursor, table_name, graph, compacted_graph_filename, leiden_output_prefix, k, m):
    best_cluster_to_id_dict = None
    best_k = 0
    best_num_subclusters = 0
    best_resolution_value = None
    for resolution_value in np.arange(0.1, 1.1, 0.1):
        cluster_to_id_dict = run_leiden(compacted_graph_filename, resolution_value, leiden_output_prefix)
        validity_and_min_k = get_validity_and_min_k(cursor, table_name, graph, cluster_to_id_dict, k, m)
        if((validity_and_min_k["is_valid"] and best_k < validity_and_min_k["min_k"]) or
           (validity_and_min_k["is_valid"] and best_k == validity_and_min_k["min_k"] and best_num_subclusters < validity_and_min_k["num_subclusters"])):
            best_cluster_to_id_dict = cluster_to_id_dict
            best_k = validity_and_min_k["min_k"]
            best_num_subclusters = validity_and_min_k["num_subclusters"]
            best_resolution_value = resolution_value
    return best_cluster_to_id_dict


def get_validity_and_min_k(cursor, table_name, graph, cluster_to_id_dict, k, m):
    clustering_validity = True
    min_k = None
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        cluster_info_dict = get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, k, m)
        clustering_validity &= cluster_info_dict["is_valid"]
        if(min_k == None):
            min_k = np.min(cluster_info_dict["k_arr"])
        else:
            min_k = np.min(min_k, np.min(cluster_info_dict["k_arr"]))
    return {
        "is_valid": clustering_validitiy,
        "min_k": min_k,
        "num_subclusters": len(cluster_to_id_dict),
    }


def get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, k, m):
    ''' equation 2 is defined by \frac{l_{s}}{L} - (\frac{d_{s}}{2L})^{2} > m where m is zero
    where l_s is the number of edges in cluster s, L is the number of edges in the
    entire network, and d_s is the total sum of the degrees of each node inside cluster s
    When this value is greater than t, it is considered a valid module in terms of modularity
    criterion. [deprecated option size b] Each cluster must also be of size at least B.
    '''
    if(len(cluster_member_arr) == 1):
        # singletons are never valid clusters
        return {
            "is_valid": False,
        }
    if(k == 0 and m == float("-inf")):
        return {
            "is_valid": True,
        }

    node_degree_valid = True
    intracluster_node_degree_arr = get_intracluster_num_degree(cursor, table_name, cluster_member_arr)
    for node,degree in intracluster_node_degree_arr:
        if(degree < k):
            node_degree_valid = False
    equation_2 = None

    use_sql = False
    if(use_sql):
        L = get_num_edges(cursor, table_name)
        l_s = get_intracluster_num_edges(cursor, table_name, cluster_member_arr)
        d_s = get_sum_num_degrees(cursor, table_name, cluster_member_arr)
        equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
    else:
        L = graph.numberOfEdges()
        equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
        for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
            int_cluster_member_arr = [int(node_id) for node_id in cluster_member_arr]
            l_s = 0
            d_s = 0
            for node in int_cluster_member_arr:
                d_s += graph.degree(node)
            for cluster_member in int_cluster_member_arr:
                for neighbor in graph.iterNeighbors(cluster_member):
                    if(neighbor in int_cluster_member_arr):
                        l_s += 1
                volume += graph.degree(cluster_member)
            l_s /= 2
            equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
    return {
       "is_valid": equation_2 >= m and node_degree_valid,
       "equation_2": equation_2,
       "k_arr": [int(tup[1]) for tup in intracluster_node_degree_arr],
    }


def run_leiden_on_cluster(cursor, table_name, graph, cluster_to_id_dict, cluster_id_to_split, output_prefix, k, m):
    ''' This runs leiden on a cluster specified by the cluster_id_to_split
    and updates the cluster_to_id_dict by creating new clusters with cluster id
    starting from the current max cluster_id  + 1.
    Note that it does erase the original cluster
    '''
    new_cluster_ids = []
    subgraph = nk.graphtools.subgraphFromNodes(graph, [int(integer_node_id) for integer_node_id in cluster_to_id_dict[cluster_id_to_split]])
    new_node_map = nk.graphtools.getContinuousNodeIds(subgraph)
    compacted_graph = nk.graphtools.getCompactedGraph(subgraph, new_node_map)
    compacted_graph_filename = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}.tsv"
    leiden_output_prefix = f"{output_prefix}/subgraph_on_cluster_{cluster_id_to_split}"
    nk.writeGraph(compacted_graph, compacted_graph_filename, nk.Format.EdgeListTabZero)
    compacted_graph_clusters = get_best_leiden(cursor, table_name, graph, compacted_graph_filename, leiden_output_prefix, k, m)
    if(compacted_graph_clusters is None):
        return None
    inverse_node_map = {new_id: old_id for old_id,new_id in new_node_map.items()}
    new_cluster_index = max(cluster_to_id_dict.keys()) + 1
    for cluster,cluster_members in compacted_graph_clusters.items():
        cluster_to_id_dict[new_cluster_index] = []
        for new_cluster_member_id in cluster_members:
            cluster_to_id_dict[new_cluster_index].append(str(inverse_node_map[int(new_cluster_member_id)]))
        new_cluster_ids.append(new_cluster_index)
        new_cluster_index += 1
    cluster_to_id_dict[current_cluster_id] = []
    return new_cluster_ids


@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the postgres connection details")
@click.option("--network", required=True, type=click.Path(exists=True), help="Integer labelled edgelist")
@click.option("--clustering", required=False, type=click.Path(exists=True), help="Initial clustering to begin with as an alternative to leiden")
@click.option("--resolution-value", required=False, type=float, help="Resolution value for Leiden")
@click.option("--k", required=False, type=int, default=0, help="The minimum connectivity among each other in a cluster to be considered valid")
@click.option("--m", required=False, type=float, default=float("-inf"), help="The minimum modularity threshold for each cluster")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def recursive_leiden(config_file, network, clustering, resolution_value, k, m, output_prefix):
    '''This is the main function that will take in a tsv integer labelled network and recursively
    run leiden on the network and its clusters until we can no longer split a cluster into its
    valid constituents where valid is defined by a positive modularity score
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    graph = nk.readGraph(network, nk.Format.EdgeListTabZero)
    cluster_to_id_dict = None

    if(clustering is None):
        initial_leiden_filename = f"{output_prefix}/initial_graph"
        cluster_to_id_dict = get_best_leiden(cursor, table_name, graph, network, initial_leiden_filename, k, m)
    else:
        cluster_to_id_dict = file_to_dict(clustering)["cluster_to_id_dict"]

    cluster_id_stack = list(cluster_to_id_dict.keys())
    with open(f"{output_prefix}/recursive_leiden.log", "w") as f:
        if(clustering is None):
            f.write(f"// No clustering was provided so we are running leiden initially\n")
        else:
            f.write(f"// An initial clustering was provided so we are not running leiden initially\n")
        f.write(f"// we start with {len(cluster_id_stack)} clusters\n")
        if(clustering is None and best_cluster_to_id_dict is None):
            f.write(f"// No leiden could produce a clustering of only valid clusters. Terminating.\n")
        elif(clustering is None and len(best_cluster_to_id_dict) == 1):
            f.write(f"// The best initial leiden failed to produce more than one cluster. Terminating.\n")


    iteration_number = 0 # this is purely for logging purposes
    while(len(cluster_id_stack) > 0):
        # print(f"A new iteration!")
        current_cluster_id = int(cluster_id_stack.pop())
        cluster_member_arr = cluster_to_id_dict[current_cluster_id]
        # array for logging and tracing purposes
        decomposed_into = []
        # print(f"-- In this iteration, we are inspecting cluster {current_cluster_id} with members {cluster_member_arr}")
        cluster_info_dict = get_cluster_info_dict(cursor, table_name, graph, cluster_member_arr, k, m)
        if(cluster_info_dict["is_valid"]):
            # print(f"-- cluster {current_cluster_id} with members {cluster_member_arr} is a valid cluster")
            new_cluster_ids = run_leiden_on_cluster(cursor, table_name, graph, cluster_to_id_dict, current_cluster_id, output_prefix, k, m)
            # extending instead of pushing every element
            if(new_cluster_ids is None):
                pass
            elif(len(new_cluster_ids) == 1):
                # the current cluster dissolved into itself
                pass
            elif(len(new_cluster_ids) > 1):
                # the current cluster has successfully decomposed into all valid clusters
                print(f"successful leiden!")
                cluster_id_stack.extend(new_cluster_ids)
        else:
            # this should never happen
            pass
            # raise Exception("cluster id stack should always only contain valid clusters")


    write_new_sorted_cluster_dict(cluster_to_id_dict, [], f"{output_prefix}/recursive_leiden_k_{k}_m_{m}")

if __name__ == "__main__":
    recursive_leiden()
