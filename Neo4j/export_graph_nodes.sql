\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

-- Using client-side copy to generate the file under the current user ownership
-- Have to do `COPY (SELECT * FROM {view}) TO` rather than simply `COPY {view} TO`
\copy (SELECT * FROM nodes) TO 'nodes.csv' (FORMAT CSV, HEADER ON)