# Cluster Processing Scripts
---
## `type_post_processing.py`
1. Process the high degree nodes (at a network level) in turn.
2. Examine all of the publications that cite A, the current high degree node.
3. Identify the clusters of each of the publications that cite A.
4. For each cluster identified in the previous step
    - 4a. If hasn't been computed already, calculate the "type 1" threshold (not all clusters need type 1 thresholds computed).
    - 4b. If A is cited by a sufficient number of publications in this cluster, add A to this cluster.

Note: Don't recompute the type 1 threshold even though the cluster membership has been updated

