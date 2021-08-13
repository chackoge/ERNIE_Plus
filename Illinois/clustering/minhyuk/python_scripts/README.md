# Python Scripts
---
## `analysis_scripts/validate_and_score_cluster.py`
The output is a score of the clustering based on each of these criteria
1. Core-covearge: the total number of core nodes
2. Non-core-to-core-connectivity: the total number of edges between core and non-core nodes

However, all input clusterings must satisfy four properties
1. Each cluster is a connected subgraph of the network
2. The core members of each cluster have at least degree k among themselves
3. Each cluster has at most b core members
4. Every non-core node is adjacent to at least one core node

## `cluster_processing_scirpts/assign_unclustered_nodes.py`
Assigns all unclustered nodes based on the given criterion. For a given node unclustered node, the cluster assignment goes to whichever cluster has the most core node to unclustered node connection. The connection can be one of in-degree, out-degree, or the sum of in and out degrees (total degree, or degree in general).

## `cluster_processing_scripts/top_down_clustering.py`
For now, all this does is take in a degree k and then output a clustering that is defined by the components of the subgraph restricted to those nodes with in-degree at least k.

## `cluster_processing_scripts/type_post_processing.py`
1. Process the high degree nodes (at a network level) in turn.
2. Examine all of the publications that cite A, the current high degree node.
3. Identify the clusters of each of the publications that cite A.
4. For each cluster identified in the previous step
    - 4a. If hasn't been computed already, calculate the "type 1" threshold (not all clusters need type 1 thresholds computed).
    - 4b. If A is cited by a sufficient number of publications in this cluster, add A to this cluster.

Note: Don't recompute the type 1 threshold even though the cluster membership has been updated

## `cluster_processing_scripts/recursive_leiden`
This script will take a given network and run leiden recursively as follows.
First it will run leiden on the whole network to determine the initial clusters.
We will keep these clusters in a stack.
Until the stack is empty, pop a cluster and do the following.
1. Check if the cluster is valid, where cluster validitiy is defined below.
2. If the cluster is valid, run leiden on the subgraph restricted to this cluster. There are three cases to consider.
    - 2a. If leiden fails to decompose the cluster, then do nothing and keep this cluster
    - 2b. If leiden fails to recover at least one cluster that is valid, then do nothing and keep this cluster
    - 2c. If leiden recovers at least one valid cluster, then push all the subclusters onto the stack, knowing that some clusters will immeditely fail the validity check and some clusters will have leiden run on them.
3. If the cluster is invalid, then we throw out this cluster and do not push anything onto the stack in this iteration.

### Cluster Validity
A cluster is valid if this inequality holds.
![](https://latex.codecogs.com/gif.latex?%5Clarge%20%5Cfrac%7Bl_%7Bs%7D%7D%7BL%7D%20-%20%28%5Cfrac%7Bd_%7Bs%7D%7D%7B2L%7D%29%5E%7B2%7D%20%3E%200)

