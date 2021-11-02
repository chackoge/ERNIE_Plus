\set ON_ERROR_STOP on
\set ECHO all

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

DROP VIEW IF EXISTS public.nodes_pubs;

CREATE OR REPLACE VIEW public.nodes_pubs AS
  WITH nodes_cte(seq_id, dimensions_id, doi, pub_year) AS (
    SELECT citing_integer_id, citing_id, citing, citing_year
      FROM dimensions.exosome_1900_2010_sabpq_deduplicated
     UNION
    SELECT cited_integer_id, cited_id, cited, cited_year
      FROM dimensions.exosome_1900_2010_sabpq_deduplicated
  )
SELECT nodes_cte.*, (mnip.integer_id IS NOT NULL) AS is_marker_node
  FROM nodes_cte
  LEFT JOIN marker_nodes_integer_pub mnip ON mnip.integer_id = nodes_cte.seq_id;

DROP VIEW IF EXISTS public.edges_pubs;

CREATE OR REPLACE VIEW public.edges_pubs AS
SELECT citing_integer_id AS citing_seq_id, cited_integer_id AS cited_seq_id
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated;

DROP VIEW IF EXISTS clusters.nodes_clusters_testing_k10_b0;

CREATE OR REPLACE VIEW clusters.nodes_clusters_testing_k10_b0 AS
SELECT cluster_no, min_k, cluster_modularity
  FROM dimensions.exosome_1900_2010_clusters e12c
  WHERE clustering_version = 'testing_k10_b0';

DROP VIEW IF EXISTS clusters.edges_clusters_testing_k10_b0;

CREATE OR REPLACE VIEW clusters.edges_clusters_testing_k10_b0 AS
SELECT cluster_no, node_seq_id
  FROM dimensions.exosome_1900_2010_cluster_nodes e12cn
  WHERE clustering_version = 'testing_k10_b0';

DROP VIEW IF EXISTS clusters.nodes_clusters_testing_k5_b0;

CREATE OR REPLACE VIEW clusters.nodes_clusters_testing_k5_b0 AS
SELECT e12c.cluster_no, e12c.min_k, e12c.cluster_modularity
  FROM dimensions.exosome_1900_2010_clusters e12c
  WHERE clustering_version = 'testing_k5_b0';

DROP VIEW IF EXISTS clusters.edges_clusters_testing_k5_b0;

CREATE OR REPLACE VIEW clusters.edges_clusters_testing_k5_b0 AS
SELECT node_seq_id, cluster_no
  FROM dimensions.exosome_1900_2010_cluster_nodes e12cn
  WHERE clustering_version = 'testing_k5_b0';

