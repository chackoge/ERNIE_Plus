MATCH (c:cluster_testing_k10_b0 {cluster_no: 1})-->(n)
RETURN n.seq_id;
