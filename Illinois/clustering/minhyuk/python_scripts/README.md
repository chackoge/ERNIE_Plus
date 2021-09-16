# Python Scripts
---
## [cluster_processing_scripts](cluster_processing_scripts)

### [cluster_processing_scripts/assign_unclustered_nodes_networkit.py](cluster_processing_scripts/assign_unclustered_nodes_networkit.py)
Assigns all unclustered nodes based on the given criterion. For a given node unclustered node, the cluster assignment goes to whichever cluster has the most core node to unclustered node connection relative to the total number of nodes in that cluster. The connection can be one of in-degree, out-degree, or the sum of in and out degrees (total degree).

In other words, for each node
1. Check how many connections it has to each cluster's core nodes given the criterion (one of in-degree, out-degree, total-degree)
2. Assign to the cluster to which the node has the largest value of value of number of connections divided by the total number of core nodes in that cluster

### [cluster_processing_scripts/recursive_graclus](cluster_processing_scripts/recursive_graclus.py)
This script will take a given network and run graclus recursively as follows, where in each graclus run the clusters are split into 2.
First it will run graclus on the whole network to determine the initial clusters if initial clusters is not provided.
We will keep these clusters in a stack.
Until the stack is empty, pop a cluster out and do the following.
1. Check if the cluster is valid, where cluster validitiy is defined below.
2. If the cluster is valid, run graclus on the subgraph restricted to this cluster. There are three cases to consider.
    - 2a. If graclus fails to decompose the cluster, then do nothing and keep this cluster
    - 2b. If graclus fails to recover at least one cluster that is valid, then do nothing and keep this cluster
    - 2c. If graclus recovers at least one valid cluster, then push the valid subclusters onto the stack
3. If the cluster is invalid, then we throw out this cluster and do not push anything onto the stack in this iteration. This can happen when the initial clustering provided has invalid clusters.

#### Cluster Validity
A cluster is valid if the inequality from equation 2 of Fortunato and Barthelemy(2007) holds.

In plain english, a cluster is valid if the difference between the number of edges in a cluster divided by the total number of edges in the graph and the squared value of the quotient of the sum of the degrees of the nodes in a cluster divided by twice the total number of eges in the graph is greater than zero.

Fortunato, Santo, and Marc Barthelemy. "Resolution limit in community detection." Proceedings of the national academy of sciences 104.1 (2007): 36-41.

