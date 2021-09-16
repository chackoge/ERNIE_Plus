\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

DROP VIEW IF EXISTS public.nodes;

-- Enter e.g., :'clustering_version'='testing_k10_b0'

CREATE OR REPLACE VIEW public.nodes AS
  WITH nodes_cte AS (
    SELECT citing_integer_id AS "seq_id:ID", citing_id AS dimensions_id, citing AS doi, citing_year AS "pub_year:short"
      FROM dimensions.exosome_1900_2010_sabpq_deduplicated
     UNION
    SELECT cited_integer_id AS "seq_id:ID", cited_id AS dimensions_id, cited AS doi, cited_year AS "pub_year:short"
      FROM dimensions.exosome_1900_2010_sabpq_deduplicated
  )
SELECT n."seq_id:ID", n.dimensions_id, n.doi, n."pub_year:short", e12cn.cluster_no, e12c.min_k, e12c.cluster_modularity
  FROM nodes_cte n
  LEFT JOIN dimensions.exosome_1900_2010_cluster_nodes e12cn
            ON (e12cn.node_seq_id = n."seq_id:ID" AND e12cn.clustering_version = :'clustering_version')
  LEFT JOIN dimensions.exosome_1900_2010_clusters e12c
            ON (e12c.cluster_no = e12cn.cluster_no AND e12c.clustering_version = e12cn.clustering_version);

DROP VIEW IF EXISTS public.edges;

CREATE OR REPLACE VIEW public.edges AS
SELECT citing_integer_id AS from_node_id, cited_integer_id AS to_node_id
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated;