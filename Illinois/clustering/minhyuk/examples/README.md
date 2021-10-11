# Examples
In this folder, we show several examples to demonstrate the effect of running kmp-parsing code on small toy networks. In all the examples, all nodes are placed in a single cluster in the input clustering.
The command used to reproduce the results is provided below.
```bash
python <kmp-parsing code>.py -e <input edgelist> -c <input clustering file> -o <output clustering file> -k 5 -p 2 -m True
```

# Definition of kmp-validity
### kmp-validity
A cluster is considered kmp-valid if it satisfies all three conditions k, m, and p.
#### k condition
k condition dictates that every core member in the cluster is adjacent to at least k other core members in the cluster.
#### m condition
m condition dictates that the cluster has a positive modularity value.
#### p condition
p condition dictates that every non-core member in the cluster is adjacent to at least p core members in the cluster.


## [no\_core](no_core)
This folder contains 2 example clusterings and networks that contain zero kmp-valid clusters at k=5 and p=2.
### [no\_core/1.clustering](no_core/1.clustering) and [no\_core/network\_1.tsv](no_core/network_1.tsv)
As shown in the diagram, network 1 is a set of nodes arranged in a line with no core substructures. The kmp-parsing code will first label nodes 0 and 5 as having the value 1 and remove them from the network. It will then label nodes 1 and 4 as having the value 1 and remove them from the network. Finally it will label the nodes 2 and 3 as having the value 1 and remove them from the network, at which point the entire network will have dissolved. Therefore, running kmp-parsing code on this input will label all input nodes as having the value 1 and will result in zero clusters returned since no set of nodes were labeled as having the value of 5, the input k value.

![](no_core/network_1.png)

*This is a graphical representation of [no\_core/network\_1.tsv](no_core/network_1.tsv), which is an edgelist that represents the network*

The log file of running kmp-parsing code for this clustering and network is saved at [no\_core/parsing\_1.out](no_core/parsing_1.out)

### [no\_core/2.clustering](no_core/2.clustering) and [no\_core/network\_2.tsv](no_core/network_2.tsv)
As shown in the diagram, network 2 consists of a single 4-clique (nodes 0, 1, 2, and 3) with node 4 adjacent to one of the nodes in the clique and node 5 adjacent to node 4. This network does not contain any core substructures at k=5 since kmp-validity at k=5 requires that every node in the core set of nodes be adjacent to at least five other core nodes. The kmp-parsing code will first label node 5 as having the value 1 and remove node 5 from the network. Node 4 will also be labelled with the value 1 and removed from the network. No nodes will be labelled with the value 2, but nodes 0 through 3 will all be labelled with the value 3 and removed from the network, at which point the entire network will have dissolved. Therefore, running kmp-parsing code on this input will result in zero clusters returned since no set of nodes were labelled as having the value 5, the input k value.

![](no_core/network_2.png)

*This is a graphical representation of [no\_core/network\_2.tsv](no_core/network_2.tsv), which is an edgelist that represents the network*

The log file of running kmp-parsing code for this clustering and network is saved at [no\_core/parsing\_2.out](no_core/parsing_2.out)

## [one\_core](one_core)
### [no\_core/3.clustering](no_core/3.clustering) and [no\_core/network\_3.tsv](no_core/network_3.tsv)
As shown in the diagram, network 3 consists of a single 6-clique (nodes 0, 1, 2, 3, 4, and 5), two nodes (nodes 11 and 12) adjacent to two nodes in the clique, and five nodes (nodes 6, 7, 8, 9, and 10) with a single edge each to the clique. This network does contain a core substructure at k=5. The 6-clique defines the core set of nodes where every node in the core set is connected to at least five other core nodes. Additionally, nodes 11 and 12 are parsed as non-core nodes at p=2 since they have at least two degrees of connection to the set of core nodes. Nodes 6 through 10 are discarded since they do not meet the non-core node criteria at p=2. The kmp-parsing code will first label nodes 6 through 10 with the value 1 and remove them from the graph. It will then label nodes 11 and 12 with the value 2 and remove them from the graph. It will not label any nodes with the value 3 or 4. As its final step, it will label nodes 0 through 5 with the value 5 and remove them from the network, at which point the entire network will have dissolved. Since there were nodes labelled with the value 5, the input k value, the kmp-parsing code will also search for nodes in the network that satisfy the p criterion. Nodes 11 and 12 meet this requirement since they both have 2 edges each to the core set of nodes. Node 11 has edges to node 0 and 1, and node 12 also has edges to node 0 and 1. The input value of p was 2, so nodes 11 and 12 meets the minimum requirement for a node to be considered a non-core node. Nodes 6 through 10 do not meet the p-adjacency requirement and are discarded. Therefore, running kmp-parsing code on this input will result in a single cluster that consists of the 6-clique and nodes 11 and 12, marking the 6-clique as the core set of nodes and marking nodes 11 and 12 as the non-core nodes.

![](one_core/network_3.png)

*This is a graphical representation of [one\_core/network\_3.tsv](one_core/network_3.tsv), which is an edgelist that represents the network*

The log file of running kmp-parsing code for this clustering and network is saved at [one\_core/parsing\_3.out](one_core/parsing_3.out). The actual clustering output containing the core nodes and its non-core nodes is saved at [one\_core/3\_parsed.clustering](one_core/3_parsed.clustering).

## [two\_cores](two_cores)
### [no\_core/4.clustering](no_core/4.clustering) and [no\_core/network\_4.tsv](no_core/network_4.tsv)
As shown in the diagram, network 4 consists of two 6-cliques with four additional nodes. Node 0 is adjacent to both the cliques with a two edges to each of the cliques. Node 1 is adjacent to both the cliques with one edge to each of the cliques. Node 2 has a single edge to one of the cliques and two edges to the other clique. Node 3 is only adjacent to node 2, which is not a part of any of the cliques. This input contains two core substructures. Each of the cliques defines a core substructure at k=5. Node 0 meets the non-core criteria at p=2, and it could be a valid non-core node of either of the cliques. Node 2 meets the non-core criteria at p=2 but it can only be a non-core member to the clique to which it has two edges. Nodes 1 and 3 do not meet the non-core criteria at p=2 since they do not have at least two edges to a set of core nodes in a cluster. The kmp-parsing code will first label node 3 with the value 1 and remove it from the graph. It will then label node 1 with the value 2 and remove it from the graph, after which node 2 will be labelled with the value 3 and removed from the graph. Node 0 will be labelled with the value 4 and removed from the graph. The rest of the nodes (nodes 4 through 9 and nodes 10 through 15) will be labelled with the value 5 and removed from the graph, leaving the network empty. Since the graph of nodes labelled with the value 5 form two separate components, each component will define the set of core nodes for a new cluster. For the cluster formed by nodes 10 through 15, node 2 will be assigned as a non-core node since node 2 has edges to nodes 12 and 13. Node 0 will be randomly assigned to one of the two clusters since it has two edges each to both the components identified. Therefore, running kmp-parsing code on this input will result in two clusters that are defined by each of the cliques and their non-core nodes.

![](two_cores/network_4.png)

*This is a graphical representation of [two\_cores/network\_4.tsv](two_cores/network_4.tsv), which is an edgelist that represents the network*

The log file of running kmp-parsing code for this clustering and network is saved at [two\_cores/parsing\_4.out](two_cores/parsing_4.out). The actual clustering output containing the core nodes and its non-core nodes is saved at [two\_cores/4\_parsed.clustering](two_cores/4_parsed.clustering).
