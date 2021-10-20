\set ON_ERROR_STOP on

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

\set ECHO all

INSERT INTO exosome_1900_2010_clusters(clustering_version, cluster_no, min_k, cluster_modularity)
SELECT DISTINCT :'clustering_version', cluster_no, min_k, cluster_modularity
  FROM stg_clusters;

INSERT INTO exosome_1900_2010_cluster_nodes(clustering_version, cluster_no, node_seq_id, is_core)
SELECT :'clustering_version', cluster_no, node_seq_id, (core_classifier = 'Core')
  FROM stg_clusters;

TRUNCATE stg_clusters;