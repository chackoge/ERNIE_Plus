CREATE OR REPLACE VIEW clusters.marker_distribution AS
SELECT cmn.marking_version, e12cn.clustering_version, e12cn.cluster_no, count(1) AS marker_count
  FROM clustering_marker_nodes cmn
  JOIN clusters.exosome_1900_2010_cluster_nodes e12cn
       ON cmn.node_seq_id = e12cn.node_seq_id
 GROUP BY cmn.marking_version, e12cn.clustering_version, e12cn.cluster_no;