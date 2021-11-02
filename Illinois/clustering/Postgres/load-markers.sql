\set ON_ERROR_STOP on

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

\set ECHO all
\copy clusters.stg_marker_nodes(row_id, node_seq_id) FROM pstdin (FORMAT csv, HEADER on)

INSERT INTO clustering_marker_nodes(marking_version, node_seq_id)
SELECT :'marking_version', node_seq_id
  FROM stg_marker_nodes;

TRUNCATE stg_marker_nodes;