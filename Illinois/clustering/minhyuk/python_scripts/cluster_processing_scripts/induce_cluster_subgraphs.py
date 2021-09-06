import click
import numpy as np
import networkit as nk

from python_scripts.utils.utils import file_to_dict

@click.command()
@click.option("--network", required=True, type=click.Path(exists=True), help="Input edge list")
@click.option("--clustering-file", required=True, type=click.Path(exists=True), help="Input clusters")
@click.option("--output-format", required=True, type=click.Choice(["edgelist", "metis"]), help="Output graph format")
@click.option("--output-prefix", required=True, type=click.Path(), help="Output file prefix")
def induce_cluster_subgraph(network, clustering_file, output_format, output_prefix):
    '''This is the main function that will take in a clustering in the format
    "<cluster number>SPACE<node id>" and output subgraphs in a defined format
    '''
    cluster_dicts = file_to_dict(clustering_file)
    cluster_to_id_dict = cluster_dicts["cluster_to_id_dict"]
    id_to_cluster_dict = cluster_dicts["id_to_cluster_dict"]
    graph = nk.readGraph(network, nk.Format.EdgeListTabZero)
    '''
    cluster_id_size_arr = []
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        if(len(cluster_member_arr) > 1):
            cluster_id_size_arr.append((cluster_id, len(cluster_member_arr)))
    sorted_cluster_id_size_arr = sorted(cluster_id_size_arr, key=lambda x: x[1])
    percentiles = [0.10, 0.25, 0.50, 0.75, 0.90, 0.99]
    with open(f"{output_prefix}/percentiles.log", "w") as f:
        for percentile in percentiles:
            sorted_cluster_id_size_arr_index = int(len(sorted_cluster_id_size_arr) * percentile)
            cluster_id = sorted_cluster_id_size_arr[sorted_cluster_id_size_arr_index][0]
            cluster_size = sorted_cluster_id_size_arr[sorted_cluster_id_size_arr_index][1]
            f.write(f"{cluster_id} has {cluster_size} elements and is the {percentile} percentile\n")
    for percentile in percentiles:
        sorted_cluster_id_size_arr_index = int(len(sorted_cluster_id_size_arr) * percentile)
        cluster_id = sorted_cluster_id_size_arr[sorted_cluster_id_size_arr_index][0]
    '''
    for cluster_id,cluster_member_arr in cluster_to_id_dict.items():
        if(len(cluster_member_arr) > 1):
            subgraph = nk.graphtools.subgraphFromNodes(graph, [int(integer_node_id) for integer_node_id in cluster_to_id_dict[cluster_id]])
            new_node_map = nk.graphtools.getContinuousNodeIds(subgraph)
            compacted_graph = nk.graphtools.getCompactedGraph(subgraph, new_node_map)
            if(output_format == "edgelist"):
                compacted_graph_filename = f"{output_prefix}/subgraph_on_cluster_{cluster_id}.tsv"
                nk.writeGraph(compacted_graph, compacted_graph_filename, nk.Format.EdgeListTabZero)
            elif(output_format == "metis"):
                compacted_graph_filename = f"{output_prefix}/subgraph_on_cluster_{cluster_id}.metis"
                nk.writeGraph(compacted_graph, compacted_graph_filename, nk.Format.METIS)
            with open(f"{output_prefix}/subgraph_on_cluster_{cluster_id}.new_to_old.map", "w") as f:
                f.write(f"new_id old_id\n")
                for old_id,new_id in new_node_map.items():
                    f.write(f"{new_id} {old_id}\n")

if __name__ == "__main__":
    induce_cluster_subgraph()
