import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict
from python_scripts.utils.sql_utils import get_cursor_client_dict,get_high_indegree_nodes_and_indegree


@click.command()
@click.option("--config-file", required=True, type=click.Path(exists=True), help="The config file containing the backbonedb and processeddb")
@click.option("--network", required=True, type=click.Path(exists=True), help="Integer labelled edgelist")
@click.option("--high-indegree-threshold", required=True, type=int, help="The minimum threshold for high in-degree nodes to be included.")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def top_down_clustering(config_file, network, high_indegree_threshold, output_prefix):
    '''This is the main function that will take in a postgres table from the config file
    and output a clustering that is identical to the components of the subgraph that is restricted
    to nodes whose indegree is at minimum the high_indegree_threshold
    '''
    cursor_client_dict = get_cursor_client_dict(config_file)
    cursor = cursor_client_dict.pop("cursor", None)
    connection = cursor_client_dict.pop("connection", None)
    table_name = cursor_client_dict.pop("table_name", None)
    graph = nk.readGraph(network, nk.Format.EdgeListTabZero)
    high_indegree_nodes = [tup[0] for tup in get_high_indegree_nodes_and_indegree(cursor, table_name, high_indegree_threshold - 1)]
    subgraph = nk.graphtools.subgraphFromNodes(graph, high_indegree_nodes)
    cc = nk.components.ConnectedComponents(subgraph)
    cc.run()
    # this is needed so that the output clustering files has ordered cluster numbers where
    # the cluster with the largest size ets assigned to cluster 0
    component_size_arr = sorted(list(cc.getComponentSizes().items()), key=lambda tup: tup[1], reverse=True)
    components = cc.getComponents()
    sequential_index_to_cluster_index_dict= {}
    with open(output_prefix + f"/{table_name}-{high_indegree_threshold}.component.clustering", "w") as f:
        sequential_index = 0
        for cluster_index,component_size in component_size_arr:
            for member in components[cluster_index]:
                f.write(f"{sequential_index} {member}\n")
            sequential_index_to_cluster_index_dict[sequential_index] = cluster_index
            sequential_index += 1

    with open(output_prefix + f"/{table_name}-{high_indegree_threshold}.component.summary", "w") as f:
        for sequential_index in range(len(component_size_arr)):
            f.write(f"{sequential_index} {cc.getComponentSizes()[sequential_index_to_cluster_index_dict[sequential_index]]}\n")

if __name__ == "__main__":
    top_down_clustering()
