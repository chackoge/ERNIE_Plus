-- BLAST Basic local alignment search tool.
-- Altschul SF, Gish W, Miller W, Myers EW, Lipman DJ.
-- J Mol Biol. 1990 Oct 5;215(3):403-10. doi: 10.1016/S0022-2836(05)80360-2.
-- PMID: 2231712 (note I had to force lower case)

--Build the a table
CREATE TABLE public.blast_a AS
SELECT citing,cited FROM open_citations
WHERE cited = lower('10.1016/S0022-2836(05)80360-2');
SELECT COUNT(1) FROM blast_b;

-- Build the b table
CREATE TABLE public.blast_b AS;

SELECT citing,cited FROM open_citations
WHERE lower(citing) = lower('10.1016/S0022-2836(05)80360-2');

-- 10.1093/comjnl/30.5.420
-- Dayhoff, 1978
-- Dayhoff M.O. (Ed.), Atlas of Protein Sequence and Structure, vol. 5, Nat. Biomed. Res. Found., Washington, DC (1978)
-- suppl. 3

-- Dayhoff M.O., Schwartz R.M., Orcutt B.C.
-- Dayhoff M.O. (Ed.), Atlas of Protein Sequence and Structure, vol. 5,
-- Nat. Biomed. Res. Found., Washington, DC (1978), pp. 345-352

-- 10.1093/nar/10.1.247
-- 10.1093/nar/14.1.57
-- 10.1126/science.2983426

-- Hardison and Margot, 1984, Hardison R.C., Margot J.B.
-- Mol. Biol. Evol., 1 (1984), pp. 302-316

-- manually insert three rows to avoid having a blank table

--CREATE sab TABLE
CREATE TABLE blast_sab AS
(SELECT DISTINCT citing AS doi FROM blast_a) UNION
(SELECT DISTINCT cited FROM blast_a) UNION
(SELECT DISTINCT citing FROM blast_b) UNION
(SELECT DISTINCT cited FROM blast_b);
CREATE INDEX blast_sab_idx ON blast_sab(doi) TABLESPACE open_citations_tbs;
--CREATE p table
CREATE TABLE blast_p AS
SELECT doi as citing,oc.cited FROM blast_sab bs
INNER JOIN open_citations oc ON
oc.citing=bs.doi;

--CREATE q table
CREATE TABLE blast_q AS
SELECT oc.citing, doi as cited FROM blast_sab bs
INNER JOIN open_citations oc ON
oc.cited=bs.doi;

-- Finally the sabpq tables
CREATE TABLE blast_sabpq_edgelist AS
(SELECT DISTINCT * FROM blast_p) UNION
(SELECT DISTINCT * FROM blast_q);
SELECT COUNT(1) FROM blast_sabpq_edgelist;

CREATE TABLE blast_sabpq_nodelist AS
(SELECT DISTINCT CITING AS node_id FROM blast_sabpq_edgelist)
UNION
(SELECT DISTINCT CITED FROM blast_sabpq_edgelist);
SELECT COUNT(1) FROM blast_sabpq_nodelist;

ALTER TABLE blast_a SET SCHEMA chackoge;
ALTER TABLE blast_b SET SCHEMA chackoge;
ALTER TABLE blast_p SET SCHEMA chackoge;
ALTER TABLE blast_q SET SCHEMA chackoge;
ALTER TABLE blast_sab SET SCHEMA chackoge;




