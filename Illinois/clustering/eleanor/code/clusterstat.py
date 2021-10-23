'''
Clustering and clusterstat classes to hold statisitcal information 
both per-cluster and about the total clustering
'''

import networkit as nk
import csv
import statistics as st

class Clustering():
    '''
    Holds information about an entire clustering on a given graph.
    Will not store nodes clustered as singletons and does not report on singletons. 
    '''

    def __init__(self, k, p, graph, clusters=None):
        self.graph=graph
        self.numberOfNodes=graph.numberOfNodes()
        self.numberOfEdges=graph.numberOfEdges()        

        self.core_graph=None

        self.clusters=dict()

        self.k_value = k
        self.p_value = p
        self.next_label = 0

        self.indicies = [0,1,2,3,4,5]
        [self.all_idx, self.k_idx, self.km_idx, self.m_idx, self.kp_idx, self.kpm_idx] = self.indicies

        self.nbr_clusters     = [ 0, 0, 0, 0, 0, 0]
        self.nbr_nodes        = [ 0, 0, 0, 0, 0, 0]
        self.total_modularity = [ 0, 0, 0, 0, 0, 0]
        self.clusters_sizes    = [None, None, None, None, None, None]
        self.clusters_ks       = [None, None, None, None, None, None]
        self.clusters_mod      = [None, None, None, None, None, None]
        self.clusters_con      = [None, None, None, None, None, None]


    def update_clustering_core(self, core_graph):
        '''
        Updates each cluster in the clustering based on the core_graph
        to set them as k-, kp-, km-, or kpm-valid and updates the clustering
        lists of valid clusters accordingly.
        '''

        self.core_graph=core_graph
        cc = nk.components.ConnectedComponents(core_graph)
        cc.run()

        for label, cluster in self.clusters.items():
            cluster.update_core_nodes(core_graph, cc)
            self.update_clustering(self.all_idx, cluster)

            if cluster.k_valid:
                self.update_clustering(self.k_idx, cluster)

                if cluster.kp_valid:
                    self.update_clustering(self.kp_idx, cluster)

            if cluster.km_valid:
                self.update_clustering(self.km_idx, cluster)
                    
                if cluster.kpm_valid:
                    self.update_clustering(self.kpm_idx, cluster)


    def update_clustering(self, i, cluster):
        '''
        Appends cluster statistical information to lists of k-, m-, km-, kp-, or 
        kpm-valid clusters so that statistics about these groupings of clusters 
        can be reported individually. i is the index for k, m, km etc as stored 
        in self.indicies. 
        '''

        self.nbr_clusters[i] += 1
        self.total_modularity[i] += cluster.modularity
        self.nbr_nodes[i] += cluster.size
    
        if self.clusters_sizes[i] == None:
            self.clusters_sizes[i] = [cluster.size]
        else:
            self.clusters_sizes[i].append(cluster.size)
    
        if self.clusters_ks[i] == None:
            self.clusters_ks[i] = [cluster.minDegree]
        else:
            self.clusters_ks[i].append(cluster.minDegree)

        if self.clusters_mod[i] == None:
            self.clusters_mod[i] = [cluster.modularity]
        else:
            self.clusters_mod[i].append(cluster.modularity)

        if self.clusters_con[i] == None:
            self.clusters_con[i] = [cluster.conductance]
        else:
            self.clusters_con[i].append(cluster.conductance)


    def generate_cluster_statistics_file(self, outfile):
        '''
        Writes information about the clustering into outfile.
        '''
        min_cluster_sizes = []
        max_cluster_sizes = []
        med_cluster_sizes = []
        mean_cluster_sizes = []

        min_cluster_ks = []
        max_cluster_ks = []
        med_cluster_ks = []
        mean_cluster_ks = []

        min_cluster_mod = []
        max_cluster_mod = []
        med_cluster_mod = []
        mean_cluster_mod = []

        min_cluster_con = []
        max_cluster_con = []
        med_cluster_con = []
        mean_cluster_con = []

        headers = ['', ' k-valid', ' m-valid', ' modular', ' kp-valid', ' kpm-valid']

        for i in range(len(headers)):
            if self.clusters_sizes[i] == None:
                min_cluster_sizes.append(None)
                max_cluster_sizes.append(None)
                med_cluster_sizes.append(None)
                mean_cluster_sizes.append(None)
            else:
                min_cluster_sizes.append(min(self.clusters_sizes[i]))
                max_cluster_sizes.append(max(self.clusters_sizes[i]))
                med_cluster_sizes.append(st.median(self.clusters_sizes[i]))
                mean_cluster_sizes.append(st.mean(self.clusters_sizes[i]))

            if self.clusters_ks[i] == None:
                min_cluster_ks.append(None)
                max_cluster_ks.append(None)
                med_cluster_ks.append(None)
                mean_cluster_ks.append(None)
            else:
                min_cluster_ks.append(min(self.clusters_ks[i]))
                max_cluster_ks.append(max(self.clusters_ks[i]))
                med_cluster_ks.append(st.median(self.clusters_ks[i]))
                mean_cluster_ks.append(st.mean(self.clusters_ks[i]))

            if self.clusters_mod[i] == None:
                min_cluster_mod.append(None)
                max_cluster_mod.append(None)
                med_cluster_mod.append(None)
                mean_cluster_mod.append(None)
            else:
                min_cluster_mod.append(min(self.clusters_mod[i]))
                max_cluster_mod.append(max(self.clusters_mod[i]))
                med_cluster_mod.append(st.median(self.clusters_mod[i]))
                mean_cluster_mod.append(st.mean(self.clusters_mod[i]))

            if self.clusters_con[i] == None:
                min_cluster_con.append(None)
                max_cluster_con.append(None)
                med_cluster_con.append(None)
                mean_cluster_con.append(None)
            else:
                min_cluster_con.append(min(self.clusters_con[i]))
                max_cluster_con.append(max(self.clusters_con[i]))
                med_cluster_con.append(st.median(self.clusters_con[i]))
                mean_cluster_con.append(st.mean(self.clusters_con[i]))

        statfile = open('{}stat.txt'.format(outfile), 'w')
        statfile.write("Congratulations. You provided the following parameter values:\n")
        statfile.write("   k = {}\n".format(self.k_value))
        statfile.write("   p = {}\n".format(self.p_value))
        statfile.write("   input network had {} nodes and {} edges.\n".format(self.numberOfNodes, self.numberOfEdges))
        statfile.write("   core coverage had {} nodes and {} edges.\n".format(self.core_graph.numberOfNodes(), self.core_graph.numberOfEdges()))
        statfile.write('\nThe algorithm produced a set of clusters (available in the CSV file), which provides the assignment of nodes to clusters, and for each cluster it says its minimum within-cluster degree, number of nodes in the cluster, modularity score of the cluster, and intra cluster conductance.\n')
        statfile.write("\nHere we provide some top-level statistics about clusterings.\n")
        for i in range(len(headers)):
            statfile.write("\n")
            statfile.write("   {}. Information about set of all{} clusters:\n".format(i+1,headers[i]))
            statfile.write("          Number of clusters: {}\n".format(self.nbr_clusters[i]))
            statfile.write("          Total modularity score: {}\n".format(self.total_modularity[i]))
            statfile.write("          Total number of nodes in clusters: {}\n".format(self.nbr_nodes[i]))
            statfile.write("          Minimum, Median, Maximum, Mean of cluster sizes: [{}, {}, {}, {}]\n".format(min_cluster_sizes[i], med_cluster_sizes[i], max_cluster_sizes[i], mean_cluster_sizes[i]))
            statfile.write("          Minimum, Median, Maximum, Mean of cluster min degree: [{}, {}, {}, {}]\n".format(min_cluster_ks[i], med_cluster_ks[i], max_cluster_ks[i], mean_cluster_ks[i]))
            statfile.write("          Minimum, Median, Maximum, Mean of cluster modularity: [{}, {}, {}, {}]\n".format(min_cluster_mod[i], med_cluster_mod[i], max_cluster_mod[i], mean_cluster_mod[i]))
            statfile.write("          Minimum, Median, Maximum, Mean of cluster conductance: [{}, {}, {}, {}]\n".format(min_cluster_con[i], med_cluster_con[i], max_cluster_con[i], mean_cluster_con[i]))
        statfile.close()


class ClusterStats():
    '''
    Holds individual cluster information
    '''
    def __init__(self, label, graph, k, p, nodes, validity_flag=True):
        self.label=label
        self.graph=graph
        self.k=k
        self.p=p
        self.minDegree=float('inf')
        self.validity_flag=validity_flag

        self.nodes=nodes
        self.size= len(nodes)

        self.coreNodes=set()
        self.nonCoreNodes=set()
        self.k_valid=False
        self.km_valid=False
        self.kp_valid=False
        self.kpm_valid=False
 
        if validity_flag:
            self.set_m_valid()
        else:
            self.m_valid=False
            self.modularity=None
            self.conductance=None

    def update_core_nodes(self,core_graph, cc):
        '''
        Updates the cluster as k, km, kp or kpm valid based on 
        the nodes present in core_graph.
        '''

        for node in self.nodes:
            if core_graph.hasNode(node):
                self.coreNodes.add(node)
            else:
                self.nonCoreNodes.add(node)
        if len(self.coreNodes) > 0:
            self.k_valid = True
            if self.modular_core(core_graph, cc):
                self.km_valid = True
            self.kp_valid = True
            for node in self.nonCoreNodes:
                core_neighbors = 0
                for neighbor in self.graph.iterNeighbors(node):
                     if neighbor in self.coreNodes:
                         core_neighbors += 1
                         if core_neighbors >= self.p:
                             break
                if core_neighbors < self.p:
                    self.kp_valid = False
            if self.kp_valid and self.km_valid:
                self.kpm_valid = True


    def modular_core(self, core_graph, cc):
        '''
        computes the modularity of the core nodes for each cluster and checks that they are connected.
        if the modularity is <= 0 or they are not connected this returns False, otherwise True. 
        '''
        if len(self.coreNodes) > 1000:
            subgraph=nk.graphtools.subgraphFromNodes(self.core_graph, self.coreNodes)
        else:
            subgraph=None

        l = self.graph.numberOfEdges()

        if subgraph == None:
            degree = 0
            for node in self.coreNodes:
                node_degree = 0
                for neighbor in self.graph.iterNeighbors(node):
                    if neighbor in self.nodes:
                        node_degree += 1
                degree += node_degree
            ls = degree / 2
        else:
            ls = subgraph.numberOfEdges()

        self.core_connected = True
        core_component = cc.componentOfNode(list(self.coreNodes).pop())
        ds = 0
        for node in self.coreNodes:
            ds += self.graph.degree(node)
            if core_component != cc.componentOfNode(node):
                self.core_connetcted = False

        self.core_modularity = (ls/l - (ds/(2*l))**2)

        return self.core_connected & (self.core_modularity > 0)


    def set_modularity(self):
        '''
        Sets the: modularity score
                  conductance and
                  minDegree of the cluster.
        Also sets the flag m-valid, based on the modularity score being > 0.
        '''

        if self.size > 1000:
            subgraph=nk.graphtools.subgraphFromNodes(self.graph, self.nodes)
        else:
            subgraph=None

        l = self.graph.numberOfEdges()
        boundary = 0

        if subgraph == None:
            degree = 0
            for node in self.nodes:
                node_degree = 0
       	        for neighbor in self.graph.iterNeighbors(node):
                    if neighbor in self.nodes:
                        node_degree += 1
                boundary += self.graph.degree(node) - node_degree
                degree += node_degree
                if node_degree < self.minDegree:
                    self.minDegree = node_degree
            ls = degree / 2
        else:
            ls = subgraph.numberOfEdges()
            for node in subgraph.iterNodes():
                boundary += self.graph.degree(node) - subgraph.degree(node)
                if subgraph.degree(node) < self.minDegree:
                    self.minDegree = subgraph.degree(node)

        ds = 0
        for node in self.nodes:
            ds += self.graph.degree(node)

        self.ds = ds
        self.ls = ls
        self.l = l

        self.modularity = (ls/l - (ds/(2*l))**2)
        self.conductance = boundary / min([ds, 2*l - ds])

    def set_m_valid(self):
        self.set_modularity()
#        print ("modularity:", self.modularity, "cluster size:", self.size, "ds:", self.ds, "ls:", self.ls , "l:", self.l) 
        if self.modularity > 0:
            self.m_valid = True
        else:
            self.m_valid = False

def read_clustering_from_file(k, p, clustering_file, graph, validity_flag=True, inverted_node_id_dict=None, cluster_node=False):
    '''
    Builds a clusterstat clustering object from the filepath clustering file.

    INPUT
    -----
    k:               Integer minimum number of other core-nodes each core node must be connected to
    p:               Integer minimum number of core-nodes each non-core node must be connected to
    clustering_file: File path for the clustering
    graph:           Networkit graph containing the original network that the clustering was generated on.
    validity_flag:   If true- the modularity will be computed for each cluster and m_valid will be updated
    inverted_node_id_dict: Contains alternative node ids if the graph id's do
                           not correspond to the clustering ids

    OUTPUT
    ------
    clustering: a clustering object containing the partition definited in clustering_file based on graph.
    '''

    clustering = Clustering(k, p, graph)
    cluster_dict = dict()
    with open(clustering_file, "r") as clust_file:
        lines = csv.reader(clust_file, dialect='excel')
        for line_arr in lines:
            if len(line_arr) == 1:
                line_arr = line_arr[0].split(' ')
            if len(line_arr) == 1:
                line_arr = line_arr[0].split('\t')
            if cluster_node: 
                node = line_arr[1]
                line_arr[1] = line_arr[0]
                line_arr[0] = node

            if line_arr[1] in cluster_dict:
                cluster_dict[line_arr[1]].append(int(line_arr[0]))
            else:
                cluster_dict[line_arr[1]] = [int(line_arr[0])]

    print (len(cluster_dict), 'clusters read')

    for label, nodes in cluster_dict.items():
        if inverted_node_id_dict != None:
            orig_nodes = []
            for node in nodes:
                orig_nodes.append(inverted_node_id_dict[node])
            nodes = orig_nodes

        if len(nodes) > 1:
            cluster = ClusterStats(label, graph, k, p, nodes, validity_flag)
            if cluster.m_valid:
                clustering.update_clustering(clustering.m_idx, cluster)

            clustering.clusters[label] = cluster

    print (len(clustering.clusters), 'non-singleton clusters read')

    return clustering
