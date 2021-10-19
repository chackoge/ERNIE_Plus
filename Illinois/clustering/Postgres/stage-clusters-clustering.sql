\set ON_ERROR_STOP on

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

-- FORMAT text
\set ECHO all
COPY stg_clusters(cluster_no, node_seq_id) FROM :'data_file' (DELIMITER ' ');