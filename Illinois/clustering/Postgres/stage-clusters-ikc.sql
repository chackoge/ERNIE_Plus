\set ON_ERROR_STOP on

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

\set ECHO all
\copy stg_clusters(node_seq_id, cluster_no, min_k, cluster_modularity) FROM pstdin (FORMAT csv)
