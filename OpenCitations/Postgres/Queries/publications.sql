-- region Metrics
SELECT max(length(uri)) AS longest_uri, max(length(issue)) AS longest_issue, max(length(volume)) AS longest_volume,
  max(length(pages)) AS longest_pages, max(length(publisher)) AS longest_publisher
FROM open_citation_pubs ocp;
-- longest_uri	longest_issue	longest_volume	longest_pages	longest_publisher
-- 105	        32	          31	            40	          262
-- 1m:37s
-- endregion