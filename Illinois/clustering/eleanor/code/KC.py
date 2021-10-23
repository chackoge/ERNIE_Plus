import argparse
import networkit as nk
import csv
import heapq as hq

def main(args):

    edge_list = args.edgeList
    out_dir = args.outDir
    b = args.maxSize
    k = args.kvalue
    
    edge_list_reader = nk.graphio.EdgeListReader('\t', 0)
    graph = edge_list_reader.read(edge_list)

    graph.removeSelfLoops()

    clusters = kc_cluster(graph, k)
    print_clusters(clusters, out_dir)


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
            (cluster, modularity_score, k) = cluster_info

            index += 1
            # print a separate line for each node in each cluster
            for node in cluster:
                csvwriter.writerow([node, index, k, modularity_score])

def kc_cluster(graph, k):
    final_clusters = []

    kc = nk.centrality.CoreDecomposition(graph, storeNodeOrder=True)
    kc.run()
    cover = kc.getCover()

    l = graph.numberOfEdges()

    subgraph = nk.graphtools.subgraphFromNodes(graph, cover.getMembers(k))

    # compute the components
    cc = nk.components.ConnectedComponents(subgraph)
    cc.run()
    components = cc.getComponents()
    print ('component sizes:', cc.getComponentSizes())

    for component in components: 
        component_graph = nk.graphtools.subgraphFromNodes(subgraph, component)
        ls = component_graph.numberOfEdges()
        ds = 0
 
        for node in component_graph.iterNodes():
            ds += graph.degree(node)

        final_clusters.append((component, ls/l - (ds/(2*l))**2, k))

    return final_clusters


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--edgeList", type=str,
                        help="Path to file containing edge lists",
                        required=True, default=None)

    parser.add_argument("-o", "--outDir", type=str,
                        help="Path to file containing output",
                        required=True, default=None)

    parser.add_argument("-k", "--kvalue", type=int,
                        help="non-negative integer value of the minimum required adjacent nodes for each node",
                        required=False, default=0)

    parser.add_argument("-b", "--maxSize", type=int,
                        help="Maximum cluster size",
                        required=False, default=-1)

    parser.add_argument("-m", "--mode", type=str,
                        help="Program mode (IKC or KC)",
                        required=False, default='IKC')

    parser.add_argument("-v", "--version", action="version", version="1.0.0",
                        help="show the version number and exit")

    return parser.parse_args()

if __name__ == "__main__":
    main(parseArgs())
