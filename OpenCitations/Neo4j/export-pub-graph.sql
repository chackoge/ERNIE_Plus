\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

-- Using client-side copy to generate the file under the current user ownership
-- Have to do `COPY (SELECT * FROM {view}) TO` rather than simply `COPY {view} TO`
\copy (SELECT doi AS "doi:ID", issn, published_year AS "year:int" FROM cr_publications cp) TO 'nodes.csv' (FORMAT CSV, HEADER ON)
\copy (SELECT oc.citing AS ":START_ID", oc.cited AS ":END_ID" FROM open_citations oc JOIN cr_publications citing_cp ON citing_cp.doi = oc.citing JOIN cr_publications cited_cp ON cited_cp.doi = oc.cited) TO 'edges.csv' (FORMAT CSV, HEADER ON)