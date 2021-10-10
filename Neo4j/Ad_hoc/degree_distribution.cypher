// Degree distribution for a cluster
MATCH (c:cluster_testing_k10_b0 {cluster_no: 1})-->(p:pub)-[r:cites]-()
WITH p.seq_id AS seq_id, count(r) as degree
RETURN degree, count(seq_id) AS nodes_count;

// Overall degree distribution
MATCH (p:pub)-[r:cites]-()
WITH p.seq_id AS seq_id, count(r) as degree
RETURN degree, count(seq_id) AS nodes_count;
// 3m:22s
