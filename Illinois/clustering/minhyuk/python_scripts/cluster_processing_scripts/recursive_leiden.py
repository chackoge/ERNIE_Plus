import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict,run_mcl,run_leiden
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_num_edges,get_sum_num_degrees,get_intracluster_num_edges


def is_valid_cluster(cursor, table_name, graph, cluster_member_arr):
   ''' equation 2 is defined by \frac{l_{s}}{L} - (\frac{d_{s}}{2L})^{2} > 0
   where l_s is the number of edges in cluster s, L is the number of edges in the
   entire network, and d_s is the total sum of the degrees of each node inside cluster s
   When this value is positive, it is considered a valid module in terms of modularity
   criterion
   '''
   L = get_num_edges(cursor, table_name)
   l_s = get_intracluster_num_edges(cursor, table_name, cluster_member_arr)
   d_s = get_sum_num_degrees(cursor, table_name, cluster_member_arr)
   equation_2 = (l_s / L) - ((d_s / (2 * L))**2)
   # print(f"-- -- for cluster {cluster_member_arr}, L={L}, l_s={l_s}, d_s={d_s}, and equation 2 = {equation_2}")
   return equation_2 > 0


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
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def recursive_leiden(config_file, network, resolution_value, output_prefix):
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
    print(f"Initially, we have {len(cluster_id_stack)} clusters")
    while(len(cluster_id_stack) > 0):
        print(f"A new iteration!")
        current_cluster_id = cluster_id_stack.pop()
        cluster_member_arr = cluster_to_id_dict[current_cluster_id]
        print(f"-- In this iteration, we are inspecting cluster {current_cluster_id} with members {cluster_member_arr}")
        if(is_valid_cluster(cursor, table_name, graph, cluster_member_arr)):
            print(f"-- cluster {current_cluster_id} with members {cluster_member_arr} is a valid cluster")
            new_cluster_ids = run_leiden_on_cluster(graph, cluster_to_id_dict, current_cluster_id, resolution_value, output_prefix)
            # extending instead of pushing every element
            at_least_one_subcluster_valid = False
            for new_cluster_id in new_cluster_ids:
                at_least_one_subcluster_valid |= is_valid_cluster(cursor, table_name, graph, cluster_to_id_dict[new_cluster_id])
            if(at_least_one_subcluster_valid and len(new_cluster_ids) > 1):
                print(f"-- cluster {current_cluster_id} with members {cluster_member_arr} has been split into {len(new_cluster_ids)}, which will be validated later")
                cluster_id_stack.extend(new_cluster_ids)
                # the current cluster has successfully decomposed into at least one valid cluster
                cluster_to_id_dict[current_cluster_id] = []
            else:
                # either the current cluster fully dissolved and we keep this cluster as it cannot go any smaller
                # or leiden returned only one cluster which is itself so we keep this cluster
                # invalidate any new cluster returend by our algorithm
                if(not at_least_one_subcluster_valid):
                    print(f"-- Cannot split cluster {current_cluster_id} consisting of {cluster_member_arr} since none of its subclusters returned by leiden is valid")
                if(len(new_cluster_ids) == 1):
                    print(f"-- Cannot split cluster {current_cluster_id} consisting of {cluster_member_arr} since leiden could not split this cluster into multiple clusters")
                for new_cluster_id in new_cluster_ids:
                    cluster_to_id_dict.pop(new_cluster_id)
                pass
        else:
            print(f"cluster {current_cluster_id} consisting of {cluster_member_arr} is not valid")


    # write_new_sorted_cluster_dict(cluster_to_id_dict, [], f"{output_prefix}/cluster_largest_cluster_{subcluster_method}_{cluster_parameter}")

if __name__ == "__main__":
    recursive_leiden()
