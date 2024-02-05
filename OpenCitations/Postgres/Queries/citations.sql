\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

-- Find a pub by a pub's other id, e.g. `doi:10.1016/j.cell.2017.07.029`
SELECT *
FROM open_citation_pub_ids ocpi
WHERE ocpi.id = '${other_id}';
-- doi:10.1016/j.cell.2017.07.029: omid:br/0640681171 -- 0.1s

-- Find # of cited works by a pub's other id, e.g. `doi:10.1016/j.cell.2017.07.029`
SELECT count(1)
FROM open_citation_pub_ids ocpi
JOIN open_citations oc ON oc.citing = ocpi.omid
WHERE ocpi.id = '${other_id}';
-- doi:10.1016/j.cell.2017.07.029: 299 -- 0.1s

-- Find # of inbound citations of the work by a pub's other id, e.g. `doi:10.1016/j.cell.2017.07.029`
SELECT count(1)
FROM open_citation_pub_ids ocpi
JOIN open_citations oc ON oc.cited = ocpi.omid
WHERE ocpi.id = '${other_id}';
-- doi:10.1016/j.cell.2017.07.029: 1511 -- 0.1s

--region Check for separation in `open_citations*` tables
SELECT *
FROM open_citations_looping
WHERE oci IN (
  SELECT oci
  FROM open_citations
);

SELECT *
FROM open_citations_parallel
WHERE oci IN (
  SELECT oci
  FROM open_citations
);

SELECT *
FROM open_citations_self
WHERE oci IN (
  SELECT oci
  FROM open_citations
);
--endregion

-- Remove total duplicates in `open_citation_duplicates`
DELETE
FROM open_citations_duplicate ocd
WHERE exists (
  SELECT 1
  FROM open_citations oc
  WHERE (oc.oci, oc.citing, oc.cited, oc.citing_pub_date, oc.time_span, oc.author_sc, oc.journal_sc)--
    IS NOT DISTINCT FROM (ocd.oci, ocd.citing, ocd.cited, ocd.citing_pub_date, ocd.time_span, ocd.author_sc,
                          ocd.journal_sc)
);
