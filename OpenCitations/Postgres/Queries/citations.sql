\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

--region Check for separation in `open_citations*` tables
SELECT *
FROM open_citation_duplicates
WHERE oci IN (SELECT oci FROM open_citations);

SELECT *
FROM open_citation_loops
WHERE oci IN (SELECT oci FROM open_citations);

SELECT *
FROM open_citation_parallels
WHERE oci IN (SELECT oci FROM open_citations);

SELECT *
FROM open_citation_self
WHERE oci IN (SELECT oci FROM open_citations);
--endregion
