CREATE OR REPLACE VIEW clusters.top_markers_by_cluster_co_occurrence AS
  /*
  For all pairs of k56 markers: find pair(s) (one or more) with the highest number of the same cluster occurrences across
  all clusterings.
  List clusters and clusterings where this pair is found.
  */
  WITH cte1 AS (
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
     WHERE cmn1.marking_version = 'k12'
     GROUP BY cmn1.marking_version, cmn1.node_seq_id, cmn2.node_seq_id
     ORDER BY cluster_co_occurrence_count DESC
     LIMIT 100
  ),
    cte2 AS (
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
       WHERE cmn1.marking_version = 'k56'
       GROUP BY cmn1.marking_version, cmn1.node_seq_id, cmn2.node_seq_id
       ORDER BY cluster_co_occurrence_count DESC
       LIMIT 100
    )
SELECT *
  FROM cte1
 UNION ALL
SELECT *
  FROM cte2;

