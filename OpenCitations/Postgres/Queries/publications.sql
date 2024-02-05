-- Find a pub by OMID, e.g. 'br/06203041400'
SELECT *
FROM open_citation_pubs ocp
WHERE omid = 'omid:${omid}';

-- Pubs without 'omid:' prefix
SELECT *
FROM open_citation_pubs ocp
WHERE left(omid, 5) <> 'omid:';
-- 0 rows
-- 24.0s

-- Total count
SELECT count(1) AS pub_count
FROM open_citation_pubs ocp;
-- 107,030,533
-- 13.6s

-- ID type distribution
SELECT left(ocp.uri, 4) AS id_prefix, count(1) AS pub_count
FROM open_citation_pubs ocp
GROUP BY left(ocp.uri, 4);

-- region Length metrics
SELECT max(length(uri)) AS longest_uri, max(length(issue)) AS longest_issue, max(length(volume)) AS longest_volume,
  max(length(pages)) AS longest_pages, max(length(publisher)) AS longest_publisher
FROM open_citation_pubs ocp;
-- longest_uri	longest_issue	longest_volume	longest_pages	longest_publisher
-- 105	        32	          31	            40	          262
-- 1m:37s
-- endregion