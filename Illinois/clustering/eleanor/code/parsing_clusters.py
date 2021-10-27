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
    graph = remove_inter_cluster_edges(graph, node_cluster, cc)

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
        modularity = get_modularity(core_graph, orig_graph, component)
        if modularity > 0 or skip_m_valid:
            if skip_m_valid and modularity > 0:
                print ("Cluster number", orig_cluster, "would be dropped ofr non-positive modularity")
            node = component[0]
            orig_cluster = node_cluster[node]
            if orig_cluster in core_comp_dict:
                core_comp_dict[orig_cluster].append(component)
            else:
                core_comp_dict[orig_cluster] = [component]
        else:
            print ("Cluster number", orig_cluster, "was dropped for non-positive modularity")

    final_clusters= []
    print ('old nbr clusters:',len(clustering.clusters),'new:', len(core_comp_dict))
    for label, components in core_comp_dict.items():
        core_node_set = set()
        for component in components:
            core_node_set.update(component)

        # if p = -1 (default) only return the core nodes
        if p >= 0:
            components = add_p_nodes(components, graph, clustering.clusters[label], p)
        for component in components:
            final_clusters.append((component, core_node_set))

    print_clusters(final_clusters, out_dir)


def remove_inter_cluster_edges(graph, node_cluster, cc):
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


def get_modularity(core_graph, graph, component):
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

def add_p_nodes(components, graph, cluster, p):
    core_node_sets = [set(component) for component in components]
    full_core_node_set = set()
    for component in components:
        full_core_node_set.update(component)
    non_core_node_sets = [set() for component in components]

    #print (full_core_node_set)

    for node in cluster.nodes:
        if node not in full_core_node_set:
            core_neighbor_counts = [0 for component in components]
            for neighbor in graph.iterNeighbors(node):
                for index in range(len(core_node_sets)):
                    if neighbor in core_node_sets[index]:
                        core_neighbor_counts[index] += 1
       
            non_core_idx = -1
            neighbor_prop = 0
            for index in range(len(core_neighbor_counts)):
                current_count = core_neighbor_counts[index]
                current_prop = current_count/len(core_node_sets[index])
                if current_prop > neighbor_prop and current_count >= p:
                    neighbor_prop = current_prop
                    non_core_idx = index
            if non_core_idx >= 0:
                non_core_node_sets[non_core_idx].add(node)

    final_components = []
    for i in range(len(components)):
        print (i, 'core:', len(core_node_sets[i]), 'non-core:', len(non_core_node_sets[i]))
        core_node_sets[i].update(non_core_node_sets[i])
        final_components.append(list(core_node_sets[i]))
    #print (components, final_components)
    return final_components


def print_clusters(clusters, out_dir):
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
            #print (core_node_set)
            index += 1
            # print a separate line for each node in each cluster
            for node in cluster:
                if node in core_node_set:
                    core_label = 'Core'
                else:
                    core_label = 'Non-Core'
                csvwriter.writerow([node, index, core_label])


def format_graph(graph1):
    origNodeIdDict = nk.graphtools.getContinuousNodeIds(graph1)
    invertedOrigNodeIdDict = dict(map(reversed, origNodeIdDict.items()))
    graph1 = nk.graphtools.getCompactedGraph(graph1, origNodeIdDict)

    if graph1.isWeighted() == False:
        print ("not weighted")
        weighted = nk.Graph(n=0, weighted=True, directed=True)

        for node in graph1.iterNodes():
            weighted.addNode()
        for u, v in graph1.iterEdges():
            if weighted.hasNode(u) == False:
                weighted.addNode(u)
            if weighted.hasNode(v) == False:
                weighted.addNode(v)
            weighted.addEdge(u, v, graph1.degreeIn(u))
            #print (u, v, graph1.degreeIn(u))
        graph = weighted
    else:
        graph = graph1
        #for u, v, w in graph1.iterEdgesWeights():
            #print (u, v, w)

    graph.removeSelfLoops()

    print (graph.numberOfNodes())
    return graph, invertedOrigNodeIdDict


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

    parser.add_argument("-f", "--clusterToNodeFormat", type=bool,
                        help="False if input file format is node_id, cluster_id on each line",
                        required=False, default=True)

    parser.add_argument("-m", "--skipMValid", type=bool,
                        help="True if you wish to bypass the positive core modularity check",
                        required=False, default=False)

    parser.add_argument("-v", "--version", action="version", version="1.0.0",
                        help="show the version number and exit")

    return parser.parse_args()

if __name__ == "__main__":
    main(parseArgs())
