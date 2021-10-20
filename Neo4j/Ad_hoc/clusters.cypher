MATCH (c:cluster_testing_k10_b0 {cluster_no: 18})-->(p:pub)
RETURN p;

// Nodes with total degrees
MATCH (:cluster_testing_k5_b0 {cluster_no: 18})-->(p:pub)-[r:cites]-()
RETURN p.seq_id, count(r) as degree
ORDER BY degree;

// Nodes with minimum total degree
MATCH (:cluster_testing_k5_b0 {cluster_no: 18})-->(p:pub)-[r:cites]-()
WITH p, count(r) as degree
WHERE count(r) >= 150
RETURN p;

// Nodes with intra-cluster degrees
MATCH (c:cluster_testing_k5_b0 {cluster_no: 18})-->(p:pub)-[r:cites]-(:pub)<--(c)
RETURN p.seq_id, count(r) as degree
ORDER BY degree;

// Nodes with minimum intra-cluster degree
MATCH (c:cluster_testing_k5_b0 {cluster_no: 18})-->(p:pub)-[r:cites]-(:pub)<--(c)
WITH p, count(r) as degree
WHERE degree >= 50
RETURN p;