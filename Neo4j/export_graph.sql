\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

COPY (SELECT
  seq_id AS "seq_id:ID(seq_id)", dimensions_id, doi, pub_year AS "pub_year:short",
  CASE WHEN is_marker_node THEN 'true' ELSE 'false' END AS "is_marker_node:boolean"
        FROM nodes_pubs) TO STDOUT (FORMAT CSV, HEADER ON)
\g 'pub.csv'

-- COPY (SELECT cluster_no AS "cluster_no:ID(testing_k10_b0_cluster_no)", min_k, cluster_modularity
--         FROM nodes_clusters_testing_k10_b0) TO STDOUT (FORMAT CSV, HEADER ON)
-- \g 'cluster_testing_k10_b0.csv'
--
-- COPY (SELECT cluster_no AS "cluster_no:ID(testing_k5_b0_cluster_no)", min_k, cluster_modularity
--         FROM nodes_clusters_testing_k5_b0) TO STDOUT (FORMAT CSV, HEADER ON)
-- \g 'cluster_testing_k5_b0.csv'
--
-- COPY (SELECT citing_seq_id AS ":START_ID(seq_id)", cited_seq_id AS ":END_ID(seq_id)"
--         FROM edges_pubs) TO STDOUT (FORMAT CSV, HEADER ON)
-- \g 'pub-cites.csv'
--
-- COPY (SELECT cluster_no AS ":START_ID(testing_k10_b0_cluster_no)", node_seq_id AS ":END_ID(seq_id)"
--         FROM edges_clusters_testing_k10_b0) TO STDOUT (FORMAT CSV, HEADER ON)
-- \g 'cluster_testing_k10_b0-contains.csv'
--
-- COPY (SELECT cluster_no AS ":START_ID(testing_k5_b0_cluster_no)", node_seq_id AS ":END_ID(seq_id)"
--         FROM edges_clusters_testing_k5_b0) TO STDOUT (FORMAT CSV, HEADER ON)
-- \g 'cluster_testing_k5_b0-contains.csv'

