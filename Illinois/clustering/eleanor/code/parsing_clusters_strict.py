import argparse
import networkit as nk
import csv
import heapq as hq
import clusterstat as cs

def main(args):

    edge_list = args.edgeList
    clusters = args.clusters
    out_dir = args.outDir
    p = args.pvalue
    k = args.kvalue
    skip_m_valid = args.skipMValid
    format = args.clusterToNodeFormat

    edge_list_reader = nk.graphio.EdgeListReader('\t', 0, continuous=True)
    orig_graph = edge_list_reader.read(edge_list)
    orig_graph.removeSelfLoops()

    clustering = cs.read_clustering_from_file(k, p, clusters, orig_graph, validity_flag=False, cluster_node=format)

    print ('orig nodes:', orig_graph.numberOfNodes())

    # build a node cluster dictionary with the clustering
    node_cluster = build_node_cluster(clustering)

    # remove singletons from the graph
    non_singletons = [node for node, cluster in node_cluster.items()]
    graph = nk.graphtools.subgraphFromNodes(orig_graph, non_singletons)

    print ('nodes:', graph.numberOfNodes())
    print ('edges:', graph.numberOfEdges())

    # compute the components
    cc = nk.components.ConnectedComponents(graph)
    cc.run()
    components = cc.getComponents()
    print ('nbr componenets',len(components))

    # remove inter cluster edges
    graph = remove_inter_cluster_edges(graph, node_cluster)

    # get the k-core decomposition and retain core nodes for k
    kc = nk.centrality.CoreDecomposition(graph, storeNodeOrder=True)
    kc.run()
    cover = kc.getCover()

    core_graph = nk.graphtools.subgraphFromNodes(graph, cover.getMembers(k))

    # compute the components
    cc = nk.components.ConnectedComponents(core_graph)
    cc.run()
    components = cc.getComponents()
    print ('nbr core componenets',len(components))

    core_comp_dict = dict()
    for component in components:
        modularity = get_core_modularity(core_graph, orig_graph, component)
        node = component[0]
        orig_cluster = node_cluster[node]
        if orig_cluster in core_comp_dict:
            core_comp_dict[orig_cluster] = None
        elif modularity <= 0 and not skip_m_valid: 
            print ("Cluster number", orig_cluster, "was dropped for non-positive core modularity")
            core_comp_dict[orig_cluster] = None
        else:
            core_comp_dict[orig_cluster] = component

    final_clusters= []
    print ('old nbr clusters:',len(clustering.clusters),'new:', len(core_comp_dict))
    for label, component in core_comp_dict.items():
        if component != None:
            core_node_set = set(component)

            if check_noncore_nodes(component, graph, clustering.clusters[label], p):
                final_clusters.append((clustering.clusters[label].nodes, core_node_set))

    print_clusters(final_clusters, out_dir, orig_graph)


def remove_inter_cluster_edges(graph, node_cluster):
    # remove inter cluster edges
    removed = 0
    cnt = 0
    remove_edges = []

    for u, v in graph.iterEdges():
        cnt += 1
        if node_cluster[u] != node_cluster[v]:
            removed += 1
            remove_edges.append((u, v))

    print ('edges checked', cnt)
    for (u, v) in remove_edges:
        graph.removeEdge(u, v)

    cc = nk.components.ConnectedComponents(graph)
    cc.run()
    components = cc.getComponents()
    print ('nbr componenets after removal',len(components))
    print ('edges:', graph.numberOfEdges(), 'removed:', removed)

    return graph


def build_node_cluster(clustering):
    #build a node cluster dictionary with the clustering
    node_cluster = dict()

    for label, cluster in clustering.clusters.items():
        for node in cluster.nodes:
            if node in node_cluster:
                print ('non-disjoint cluster error')
            node_cluster[node] = label

    return node_cluster


def get_core_modularity(core_graph, graph, component):
    l = graph.numberOfEdges()
    if l < 1:
        return -1

    ls = 0
    ds = 0

    for node in component:
        ls += core_graph.degree(node)
        ds += graph.degree(node)
    ls = ls/2

    return (ls/l - (ds/(2*l))**2)


def check_noncore_nodes(component, graph, cluster, p):
    if p < 0: 
        if len(component) == len(cluster.nodes):
            return True
        else:
            return False

    core_node_set = set(component)
    non_core_node_set = set()

    for node in cluster.nodes:
        if node not in core_node_set:
            core_neighbor_count = 0
            for neighbor in graph.iterNeighbors(node):
                if neighbor in core_node_set:
                    core_neighbor_count += 1

            if core_neighbor_count < p:
                return False

    return True


def print_clusters(clusters, out_dir, orig_graph):
    '''
    This writes a csv containing lines with the:
    node Id, cluster nbr, and value of k for which cluster nbr was generated
    
    INPUT
    -----
    clusters : a list of clusters represented as lists of nodes in each cluster
    outDir : the file path and name of the ouput
    '''
    # the index indicates the order for when the cluster number was generated
    index = 0
    k = 0
    with open("{}".format(out_dir), "w") as output:
        csvwriter = csv.writer(output)
        for cluster_info in clusters:
            (cluster, core_node_set) = cluster_info
            modularity = get_modularity(cluster, orig_graph)
            #print (core_node_set)
            index += 1
            # print a separate line for each node in each cluster
            for node in cluster:
                if node in core_node_set:
                    core_label = 'Core'
                else:
                    core_label = 'Non-Core'
                csvwriter.writerow([node, index, core_label, modularity])



def get_modularity(cluster, graph):

    if len(cluster) > 1000:
        subgraph=nk.graphtools.subgraphFromNodes(graph, cluster)
    else:
        subgraph=None

    l = graph.numberOfEdges()
    if l < 1:
        return -1

    cluster_set = set(cluster)

    ls = 0
    ds = 0

    if subgraph == None:
        intra_cluster_degree = 0
        for node in cluster:
            ds += graph.degree(node)
            ic_node_degree = 0
            for node2 in cluster_set:
                if graph.hasEdge(node, node2) or graph.hasEdge(node2, node):
                    ic_node_degree += 1
            intra_cluster_degree += ic_node_degree
        ls = intra_cluster_degree / 2
    else:
        ls = subgraph.numberOfEdges()
        for node in cluster:
            ds += graph.degree(node)

    #print ("l", l, "ls", ls, "ds", ds)

    return (ls/l - (ds/(2*l))**2)


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

    parser.add_argument("-k", "--kvalue", type=int,
                        help="non-negative integer value of the minimum required adjacent nodes for each node",
                        required=False, default=0)

    parser.add_argument("-p", "--pvalue", type=int,
                        help="Non-negative integer value of the number of core memebers a non-core node must be adjacent to",
                        required=False, default=-1)

    parser.add_argument("-f", "--clusterToNodeFormat", type=str2bool,
                        help="False if input file format is node_id, cluster_id on each line",
                        required=False, default=True)

    parser.add_argument("-m", "--skipMValid", type=str2bool,
                        help="True if you wish to bypass the positive core modularity check",
                        required=False, default=False)

    parser.add_argument("-v", "--version", action="version", version="1.0.0",
                        help="show the version number and exit")

    return parser.parse_args()

def str2bool(b):
    if isinstance(b, bool):
       return b
    if b.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif b.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    main(parseArgs())
