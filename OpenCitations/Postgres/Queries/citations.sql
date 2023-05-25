\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

--region Check for separation in `open_citations*` tables
SELECT *
FROM open_citation_loops
WHERE oci IN (SELECT oci
              FROM open_citations);

SELECT *
FROM open_citation_parallels
WHERE oci IN (SELECT oci
              FROM open_citations);

SELECT *
FROM open_citation_self
WHERE oci IN (SELECT oci
              FROM open_citations);
--endregion

-- Remove total duplicates in `open_citation_duplicates`
DELETE
FROM open_citation_duplicates ocd
WHERE exists (SELECT 1
              FROM open_citations oc
              WHERE (oc.oci, oc.citing, oc.cited, oc.creation_date, oc.time_span, oc.author_sc,
                     oc.journal_sc) IS NOT DISTINCT FROM (ocd.oci, ocd.citing, ocd.cited, ocd.creation_date,
                                                          ocd.time_span,
                                                          ocd.author_sc,
                                                          ocd.journal_sc));
