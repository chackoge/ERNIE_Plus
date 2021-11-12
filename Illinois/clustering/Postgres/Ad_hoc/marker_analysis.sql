CREATE OR REPLACE VIEW clusters.cluster_markers AS
  /*
  For all pairs of k56/k12 markers: find a number of the same cluster occurrences across all clusterings.
  List clusters and clusterings where this pair is found.
  */
SELECT
  cmn1.marking_version, cmn1.node_seq_id AS node_seq_id1, cmn2.node_seq_id AS node_seq_id2,
  count(1) AS cluster_co_occurrence_count,
  array_agg(e12cn1.clustering_version || ': cluster #' || e12cn1.cluster_no) AS cluster_list
  FROM clusters.clustering_marker_nodes cmn1
  JOIN clusters.clustering_marker_nodes cmn2
       ON cmn2.marking_version = cmn1.marking_version AND cmn2.node_seq_id > cmn1.node_seq_id
  JOIN exosome_1900_2010_cluster_nodes e12cn1
       ON e12cn1.node_seq_id = cmn1.node_seq_id
  JOIN exosome_1900_2010_cluster_nodes e12cn2
       ON e12cn2.clustering_version = e12cn1.clustering_version AND e12cn2.cluster_no = e12cn1.cluster_no
           AND e12cn2.node_seq_id = cmn2.node_seq_id
 GROUP BY cmn1.marking_version, cmn1.node_seq_id, cmn2.node_seq_id;

CREATE OR REPLACE VIEW clusters.high_co_occurrence_k12_marker_pairs AS
-- Pairs co-occurring in all clusterings
SELECT cm.node_seq_id1, mnip1.doi AS doi1, cm.node_seq_id2, mnip2.doi AS doi2, cm.cluster_list
  FROM clusters.cluster_markers cm
  JOIN public.marker_nodes_integer_pub mnip1 ON mnip1.integer_id = cm.node_seq_id1
  JOIN public.marker_nodes_integer_pub mnip2 ON mnip2.integer_id = cm.node_seq_id2
WHERE cm.marking_version = 'k12' AND cm.cluster_co_occurrence_count >= 12;

CREATE OR REPLACE VIEW clusters.high_co_occurrence_k56_marker_pairs AS
-- Pairs co-occurring in all clusterings
SELECT cm.node_seq_id1, mnip1.doi AS doi1, cm.node_seq_id2, mnip2.doi AS doi2, cm.cluster_list
  FROM clusters.cluster_markers cm
  JOIN public.marker_nodes_integer_pub mnip1 ON mnip1.integer_id = cm.node_seq_id1
  JOIN public.marker_nodes_integer_pub mnip2 ON mnip2.integer_id = cm.node_seq_id2
WHERE cm.marking_version = 'k56' AND cm.cluster_co_occurrence_count >= 12;

