'''
Generates cluster statistics file from an edgelist and clustering 
(clustering formatted as one node per line with first column node number and second column cluster number)

Will show information about k-valid, kp-valid, m-valid, km-valid, and kpm-valid clusters in the given clustering.
'''

import argparse
import networkit as nk
import csv
import clusterstat as cs
import heapq as hq
import statistics as st

def main(args):

    edge_list = args.edgeList
    clusters = args.clusters
    out_dir = args.outDir
    p_value = args.p_value
    k_value = args.k_value

    print ('Reading Graph')

    edge_list_reader = nk.graphio.EdgeListReader('\t', 0)
    orig_graph = edge_list_reader.read(edge_list)
    orig_graph.removeSelfLoops()
    
    if p_value == -1:
        p_value = orig_graph.numberOfNodes()

    print ('Building clustering statistics')

    clustering = cs.read_clustering_from_file(k_value, p_value, clusters, orig_graph)

    print ('Extracting k-Core from clusters')

    core_graph = build_core_graph(orig_graph, k_value, clustering)

    print ('Updating k-Core statistics')

    clustering.update_clustering_core(core_graph)

    print ('Printing clustering kpm statistics')

    #for label, cluster in clustering.clusters.items():
    #    print ('cluster #:', label, "modularity score:", cluster.modularity)

    clustering.generate_cluster_statistics_file(out_dir)


def build_core_graph(orig_graph, k, clustering):
    '''
    INPUT
    -----
    graph:      networkit graph that is the full network read from edgelist
                self loops must already be removed
    k:          the minimum number of core nodes that each core node must also be conneced to
    clustering: the clusterstat clustering object, representing the clustering

    OUTPUT
    ------
    core_graph: the subgraph where all nodes are all at least k connected
    '''

    node_cluster = dict()
    labels = set()
    for label, cluster in clustering.clusters.items():
        labels.add(label)
        for node in cluster.nodes:
            if node in node_cluster:
                print ('non-disjoint cluster error')
            node_cluster[node] = label

    non_singletons = [node for node, cluster in node_cluster.items()]
    graph = nk.graphtools.subgraphFromNodes(orig_graph, non_singletons)

    print (graph.numberOfNodes(), 'nodes left after removing singletons')
    print (graph.numberOfEdges(), 'Egdes in non-singleton clusters')

    print ('Removing inter-cluster edges')
    # remove inter cluster edges
    removed = 0
    cnt = 0
    remove_edges = []
    for u, v in graph.iterEdges():
        cnt += 1
        if node_cluster[u] != node_cluster[v]:
            removed += 1
            remove_edges.append((u, v))

    print ('edges checked for removal: ', cnt)
    for (u, v) in remove_edges:
        graph.removeEdge(u, v)

    print ('edges left:', graph.numberOfEdges(), 'edges removed:', removed)
    kc = nk.centrality.CoreDecomposition(graph, storeNodeOrder=True)
    kc.run()
    cover = kc.getCover()

    core_graph = nk.graphtools.subgraphFromNodes(graph, cover.getMembers(k))
    print ('nodes:', graph.numberOfNodes(), 'core nodes', core_graph.numberOfNodes())

    return core_graph
    

def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--edgeList", type=str,
                        help="Path to file containing edge lists",
                        required=True, default=None)

    parser.add_argument("-o", "--outDir", type=str,
                        help="Path to file containing output",
                        required=True, default=None)
                        
    parser.add_argument("-c", "--clusters", type=str,
                        help="Path to file containing node clusterings",
                        required=True, default=None)

    parser.add_argument("-k", "--k_value", type=int,
                        help="Minimum intracluster node degree",
                        required=True, default=0)
                        
    parser.add_argument("-p", "--p_value", type=int,
                        help="Minimum number of core nodes non-core nodes must be connected to",
                        required=False, default=-1)

    parser.add_argument("-v", "--version", action="version", version="1.0.0",
                        help="show the version number and exit")

    return parser.parse_args()

if __name__ == "__main__":
    main(parseArgs())
