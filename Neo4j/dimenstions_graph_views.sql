\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

DROP VIEW IF EXISTS public.nodes;

CREATE OR REPLACE VIEW public.nodes AS
SELECT citing_integer_id AS "seq_id:ID", citing_id AS dimensions_id, citing AS doi, citing_year AS "pub_year:short"
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated
 UNION
SELECT cited_integer_id AS "seq_id:ID", cited_id AS dimensions_id, cited AS doi, cited_year AS "pub_year:short"
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated;

DROP VIEW IF EXISTS public.edges;

CREATE OR REPLACE VIEW public.edges AS
SELECT citing_integer_id AS from_node_id, cited_integer_id AS to_node_id
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated;