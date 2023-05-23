\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

--ALTER TABLE open_citations SET LOGGED;

--CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations (cited) TABLESPACE open_citations_tbs;

ANALYZE VERBOSE open_citations;