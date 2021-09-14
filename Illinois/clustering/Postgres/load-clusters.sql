\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

-- Enter e.g., :'data_dir'='/srv/local/shared/external/for_eleanor/gc_exosome/', :'cluster_filename'='testing_k5_b0'

--@formatter:off
COPY dimensions.stg_clusters(node_seq_id, cluster_no, min_k, cluster_modularity) --
  FROM :'data_dir'
    :'cluster_filename'
    '.csv' (FORMAT CSV);
--@formatter:on

INSERT INTO dimensions.exosome_1900_2010_clusters(clustering_version, cluster_no, min_k, cluster_modularity)
SELECT DISTINCT :'cluster_filename', cluster_no, min_k, cluster_modularity
  FROM dimensions.stg_clusters;

INSERT INTO dimensions.exosome_1900_2010_cluster_nodes(clustering_version, cluster_no, node_seq_id)
SELECT :'cluster_filename', cluster_no, node_seq_id
  FROM dimensions.stg_clusters;

TRUNCATE dimensions.stg_clusters;