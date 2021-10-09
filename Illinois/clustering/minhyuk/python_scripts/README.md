# Python Scripts
---
## How to Run
Once you clone the git repository,
```console
foo@bar:~$ export PYTHON_PATH="<path to the minhyuk folder>:$PYTHON_PATH"
foo@bar:~$ python -m python_scripts.<folder name>.<script name> --help
```
For example,
```console
foo@bar:~$ export PYTHON_PATH="/home/foo/git_repos/ERNIE_Plus/Illinois/clustering/minhyuk/:$PYTHON_PATH"
foo@bar:~$ python -m python_scripts.cluster_processing_scripts.recursive_graclus name --help
```
The scripts are dependent on
- `click`
- `matplotlib`
- `networkit`
- `numpy`
- `psycopg2-binary`

## File Formats
### Network edgelist
Some scripts require a tab separated integer node edgelist. The format for the network edge list is shown below. The example below shows 6 edges where the edge direction is from the first column to the second column. Node 1 has an edge to node 2 and node 3 while node 2 has an edge to node 3 only. The nodes 4, 5, and 5 form a cycle.
```csv
1   2
2   3
1   3
4   5
5   6
6   4
```
### config.json
Some scripts require a config.json file in the directory where the python command was issued. The format for the config.json is shown below.
```json
{
    "dbname": "<psql database name>",
    "user": "<psql username>",
    "table_name": "<schema.edgelist_tablename>",
    "node_table_name": "<schema.nodelist_tablename>"
}
```
### Clustering
Some scripts require a clustering file of cluster ids to integer node ids. The format for the clustering file is shown below. The example below shows 2 clusters with nodes 1,2, and 3 belonging to cluster 0 and nodes 4,5, and 6 belonging to cluster 1.
```csv
0 1
0 2
0 3
1 4
1 5
1 6
```
### Core nodes
Some scripts require a core nodes file of integer node ids. The format for the clustering file is shown below. The example below shows 3 core nodes with node ids 1, 4, and 5.
```csv
1
4
5
```


## [cluster_processing_scripts](cluster_processing_scripts)

### [cluster_processing_scripts/merge_clusterings.py](cluster_processing_scripts/merge_clusterings.py)
This script merges all the clusterings provided in the input folder and writes one merged clustering output

### [cluster_processing_scripts/generate_save_for_later.py](cluster_processing_scripts/generate_save_for_later.py)
This script generates the save\_for\_later(j) clusters given the clustering from the previous iteration and the clustering from the current iteration. The previous iteration and current iteration is expected to contain only kmp-valid clusters, and the current iteration is the set of kmp-valid clusters, or the core components, of the result of running graclus on the previous iteration clustering.

The save\_for\_later(j) clustering then contains all the clusters that were not decomposed into kmp-valid clusters from the previous iteration to the current iteration.

For every cluster in the current iteration of clustering,
1. a representative node is chosen
2. the cluster in the previous iteration that contains the representative node is marked

After processing all the clusters in the current iteration of clustering, those clusters in the previous clustering that have never been marked are the ones that end up in the save for later clustering.

### [cluster_processing_scripts/assign_unclustered_nodes.py](cluster_processing_scripts/assign_unclustered_nodes.py)
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
A cluster is valid if the inequality from equation 2 of Fortunato and Barthelemy(2007) holds and if every node in the cluster has intracluster degree of at least k.

In plain english, Fortunato and Barthelemy(2007) definition implies that a cluster is valid if the difference between the number of edges in a cluster divided by the total number of edges in the graph and the squared value of the quotient of the sum of the degrees of the nodes in a cluster divided by twice the total number of eges in the graph is greater than zero.

Fortunato, Santo, and Marc Barthelemy. "Resolution limit in community detection." Proceedings of the national academy of sciences 104.1 (2007): 36-41.

