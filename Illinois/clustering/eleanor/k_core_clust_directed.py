import sys
import os
import shutil
import json
import time
import argparse
import node as nd
import heapq
import copy
import networkx as nx
import matplotlib.pyplot as plt
import csv
from collections import deque
from copy import deepcopy


def main(args):

    edge_list = args.edgeList
    outDir = args.outDir
    max_cluster_size = args.maxNodes

    # read edgelist and build nodes.
    node_dict = build_node_dict(edge_list)

    nbr_nodes = len(node_dict)
    nbr_clustered_nodes = 0
    print (nbr_nodes, " total nodes in network")
    cluster_index = 0
    
    # compute the components before k-core
    components, clusters, singletons, cluster_index, nbr = get_components(node_dict, max_cluster_size, cluster_index)
    
    nbr_clustered_nodes += nbr
    print (nbr_clustered_nodes/nbr_nodes , " percent of nodes clustered ; ", nbr_clustered_nodes, "/", nbr_nodes, " (", len(singletons), " singletons)")

    # use k-core decomposition on every componenet found
    while components:
        component = components.pop()
        sub_components = [component]
        k = component.get_min_degree()
        k_core_removed_nodes = set()
        original_size = component.get_size()
        
        # since we remove edges in k-core (backup the edge lists)
        for label, node in component.get_node_dict().items():
            node.save_node()
        
        # start k-core decomosition incrementing k until the graph is disolved
        # or the minumum cluster size has been reached for all sub components
        # (where sub-components are the new components k-core decomposition might create)
        while sub_components:
            component = sub_components.pop()
            node_dict = component.get_node_dict()
 
            k += 1
            print (len(node_dict), " nodes remaining")
            
            # find the singletons and remaining nodes after k-core
            removed_singletons = k_core(k, node_dict)
            
            # recompute the components of the remaining nodes and update the componet lists or dictionaries
            new_components, new_clusters, new_singletons, cluster_index, nbr = get_components(node_dict, max_cluster_size, cluster_index)
            sub_components.extend(new_components)
            clusters.update(new_clusters)
            singletons.extend(new_singletons)
            
            nbr_clustered_nodes += nbr
            print (nbr_clustered_nodes/nbr_nodes , " percent of nodes clustered ; ", nbr_clustered_nodes, "/", nbr_nodes, " (", len(singletons), " singletons)")

            # save the k-core removed nodes
            k_core_removed_nodes.update(removed_singletons)

        # if k-core didn't produce any new clusters add removed nodes to the singleton list
        # otherwise re-build a component of the removed nodes and find the next most 
        # densely connected k-core cluster among them
        if len(k_core_removed_nodes) == original_size:
            singletons.extend(k_core_removed_nodes)
        else:
            node_dict = dict()
            print ('nbr k-core removed nodes : ' ,len(k_core_removed_nodes))
            
            # rebuild the component with any removed singleton nodes (also rebuilding the edges)
            for node in k_core_removed_nodes:
                node.reset_node()
                for neighbor in node.get_neighbors():
                    if neighbor not in k_core_removed_nodes: 
                        node.remove_edges(neighbor)
                node_dict[node.get_label()] = node

            # recompute the components since the removed nodes might form multiple components
            new_components, new_clusters, new_singletons, cluster_index, nbr = get_components(node_dict, max_cluster_size, cluster_index)
            components.extend(new_components)
            clusters.update(new_clusters)
            singletons.extend(new_singletons)
            
            nbr_clustered_nodes += nbr
            print (nbr_clustered_nodes/nbr_nodes , " percent of nodes clustered ; ", nbr_clustered_nodes, "/", nbr_nodes , " (", len(singletons), " singletons)")

    # build output file
    print_clusters(clusters, singletons, outDir, cluster_index)

def print_clusters(clusters, singletons, outDir, cluster_index):
    '''
    INPUT
    -----
    clusters: dictionary where label = cluster number and value = node dictionary (node label key and node object value)
    singletons: a list of nodes in their own cluster
    outDir: file path for ouput
    cluster_index: index of the last used non singleton cluster
    '''
    with open("{}".format(outDir), "w") as output:
        csvwriter = csv.writer(output)
        for index, cluster in clusters.items():
            node_dict = cluster.get_node_dict()
            for label, node in node_dict.items():
                csvwriter.writerow([label, index])
        for node in singletons:
            csvwriter.writerow([node.get_label(), cluster_index, "singleton"])
            cluster_index += 1


def k_core(max_degree, node_dict):
    '''
    INPUT
    -----
    max_degree: integer value k of largest node degree allowed in the resulting graph
    node_dict: dictionary where key = node label and value = node
    
    OUTPUT
    ------
    removed_nodes: a list of the nodes removed in k-core
    (also updates the node_dict with the remaining nodes after k-core)
    '''
    removed_nodes = []
    queue = []
    queued = set()
    counter = 0

    # first add every node of degree < max_degree to a queue
    for label, node in node_dict.items():
        if node.get_in_degree() <= max_degree:
            heapq.heappush(queue, [node.get_in_degree(), counter, node])
            counter += 1
            queued.add(node)
    degree = 0
    while queue:
        try:
            degree, _, node = heapq.heappop(queue)
        except IndexError:
            break

        if degree <= max_degree:
            if node.get_label() in node_dict:
                # remove the node
                removed_nodes.append(node)
                node_dict.pop(node.get_label())
                
                for neighbor in node.get_neighbors():
                    # remove the incident edges
                    neighbor.remove_edges(node)
                    
                    # add neighboring nodes that are now less than the max_degree if not already queued
                    if neighbor.get_in_degree() <= max_degree:
                        if neighbor not in queued:
                            heapq.heappush(queue, [neighbor.get_in_degree(), counter, neighbor])
                            counter += 1
                            queued.add(neighbor)

    return removed_nodes


def get_components(node_dict, max_cluster_size, final_index):
    '''
    INPUT
    -----
    node_dict: dictionary where key = node label and value = node
    max_cluster_size: integer value of largest allowed resulting cluster
    final_index: current cluster nbr to be used and incrementally updated
    
    OUTPUT
    ------
    components: a list of components that are larger than the max_cluster_size
    final_clusters: a dictioanry where key = cluster index and value = a component
    singletons: a list of nodes that form individual components
    final_index: the next usable cluster number 
    nbr: the total number of nodes that have been put into singletons or final_clusters
    '''
    components = []
    final_clusters = dict()
    singletons = []
    nbr = 0

    # nodes from node_dict will be removed as they are added to a component in
    # build_component() so node_dict contains all nodes not put into a component 
    while node_dict:
        node_label = next(iter(node_dict))
        node = node_dict[node_label]
        component = build_component(node, node_dict)
        
        # use the size of the resulting component to determine if it is a 
        # final_cluster, singleton, or a component still to be processed
        if component.get_size() < 2:
            singletons.append(node)
            nbr += 1
        elif component.get_size() < max_cluster_size:
            final_clusters[final_index] = component
            final_index += 1
            nbr += component.get_size()
            print("component size :",component.get_size())
        else:
            components.append(component)

    return components, final_clusters, singletons, final_index, nbr


def build_component(node, node_dict):
    '''
    INPUT
    -----
    node: the seed node for the component 
    node_dict: dictionary where key = node label and value = node
    
    OUTPUT
    ------
    component: a Component obect containing a node dict of the nodes connected to seed node
    (also removes the nodes used in the component from node_dict)
    '''
    component = nd.Component(node)
    queue = deque([node])
    queued = {node}

    # dfs of connected nodes
    while queue:
        node = queue.pop()
        node_dict.pop(node.get_label(), None)
        component.update(node)
        for neighbor in node.get_neighbors():
            if neighbor not in queued:
                queue.append(neighbor)
                queued.add(neighbor)

    return component


def build_node_dict(edge_list):
    '''
    INPUT 
    -----
    edge_list: the file path to the csv containing directed edges 
               (out node : left, in node : right)
    
    OUTPUT
    ------
    node_labels: a dictionary where keys = node labels
                 and values are node objects
    '''
    node_labels = dict()

    with open(edge_list, 'r') as file:
        lines = csv.reader(file, dialect='excel')
        
        for line_arr in lines:

            edge_nodes = dict()
            for i in range(2):
                if line_arr[i] in node_labels:
                    edge_nodes[i] = node_labels[line_arr[i]]
                else:
                    edge_nodes[i] = nd.Node(line_arr[i])
                    node_labels[line_arr[i]] = edge_nodes[i]

            edge_nodes[0].add_out_degree(edge_nodes[1])
            edge_nodes[1].add_in_degree(edge_nodes[0])

        return node_labels


def parseArgs():
    parser = argparse.ArgumentParser()


    parser.add_argument("-m", "--maxNodes", type=int,
                        help="Maximum nodes per cluster", required=True, default=1000)

    parser.add_argument("-e", "--edgeList", type=str,
                        help="Path to file containing edge lists", required=True, default=None)

    parser.add_argument("-o", "--outDir", type=str,
                        help="Path to file containing output", required=True, default=None)

    parser.add_argument("-v", "--version", action="version", version="1.0.0", help="show the version number and exit")

    return parser.parse_args()

if __name__ == "__main__":
    main(parseArgs())
