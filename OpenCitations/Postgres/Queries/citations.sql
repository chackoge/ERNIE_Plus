-- Delete self-citations
DELETE
  FROM open_citations
 WHERE oci IN (
   SELECT oci
     FROM open_citations_invalid
    WHERE
      -- Self-citations
      citing = cited
 );

-- Parallel citations
SELECT *
  FROM open_citations_invalid
WHERE citing <> cited;

SELECT oc.citing, oc.cited
  FROM open_citations oc
  JOIN cr_publications citing_cp
       ON citing_cp.doi = oc.citing
  JOIN cr_publications cited_cp
       ON cited_cp.doi = oc.cited;

INSERT INTO open_citations(oci, citing, cited, time_span, creation_date)
SELECT oci, citing, cited, time_span, creation_date
  FROM ernieplus.public.open_citations
 LIMIT 1
    ON CONFLICT (oci) DO UPDATE SET citing = excluded.citing,
      cited = excluded.cited,
      time_span = excluded.time_span,
      creation_date = excluded.creation_date;