\set ON_ERROR_STOP on
\set ECHO all

-- DataGrip: start execution from here
SET TIMEZONE = 'US/Eastern';

SELECT clustering_version, count(1) AS num_clusters
FROM clusters.exosome_1900_2010_clusters
GROUP BY clustering_version;