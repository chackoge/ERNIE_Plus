--CREATE s TABLE (I used command line) for \COPY
\COPY public.europepmc_1990_2010_s FROM 'europepmc_1990_2010_ids.csv' WITH(FORMAT CSV, HEADER);

--CREATE a TABLE (cites s)
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_a;
CREATE TABLE public.europepmc_exosome_1990_2010_a AS
SELECT oc.citing, e12s.doi AS cited
FROM open_citations oc
INNER JOIN europepmc_exosome_1990_2010_s e12s
ON oc.cited=e12s.doi;

--CREATE b Table (is cited by s)
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_b;
CREATE TABLE europepmc_exosome_1990_2010_b AS
SELECT e12s.doi AS citing ,oc.cited FROM open_citations oc
INNER JOIN europepmc_exosome_1990_2010_s e12s
ON oc.citing=e12s.doi;

--CREATE s-a-b list of nodes
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_sab;
CREATE TABLE europepmc_exosome_1990_2010_sab AS
SELECT DISTINCT citing as doi FROM europepmc_exosome_1990_2010_a UNION
SELECT DISTINCT cited FROM europepmc_exosome_1990_2010_a UNION
SELECT DISTINCT citing FROM europepmc_exosome_1990_2010_b UNION
SELECT DISTINCT cited FROM europepmc_exosome_1990_2010_a UNION
SELECT DISTINCT doi FROM europepmc_exosome_1990_2010_s;
CREATE INDEX europepmc_exosome_1990_2010_sab_idx
ON europepmc_exosome_1990_2010_sab(doi) TABLESPACE open_citations_tbs;
SELECT COUNT(1) from europepmc_exosome_1990_2010_sab;

--CREATE p TABLE
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_p;
CREATE TABLE europepmc_exosome_1990_2010_p AS
SELECT oc.citing,ee12s.doi as cited
FROM europepmc_exosome_1990_2010_sab ee12s
INNER JOIN open_citations oc
ON oc.cited=ee12s.doi;

-- CREATE q TABLE
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_q;
CREATE TABLE europepmc_exosome_1990_2010_q AS
SELECT ee12s.doi as citing, oc.cited
FROM europepmc_exosome_1990_2010_sab ee12s
INNER JOIN open_citations oc
ON oc.citing=ee12s.doi;

SELECT COUNT(1) FROM europepmc_exosome_1990_2010_q;

-- FINALLY sabq table
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_sabpq_edgelist;
CREATE TABLE europepmc_exosome_1990_2010_sabpq_edgelist AS
(SELECT DISTINCT * FROM europepmc_exosome_1990_2010_p)
UNION
(SELECT DISTINCT * from europepmc_exosome_1990_2010_q);
SELECT COUNT(1) FROM europepmc_exosome_1990_2010_sabpq_edgelist;

-- sabpq nodelist
DROP TABLE IF EXISTS europepmc_exosome_1990_2010_sabpq_nodelist;
CREATE TABLE europepmc_exosome_1990_2010_sabpq_nodelist
AS (SELECT DISTINCT citing as node_id from europepmc_exosome_1990_2010_sabpq_edgelist)
UNION
(SELECT DISTINCT cited from europepmc_exosome_1990_2010_sabpq_edgelist);
CREATE INDEX europepmc_exosome_1990_2010_sabpq_nodelist_idx
ON europepmc_exosome_1990_2010_sabpq_nodelist(node_id) TABLESPACE open_citations_tbs;
SELECT COUNT(1) FROM europepmc_exosome_1990_2010_sabpq_nodelist;