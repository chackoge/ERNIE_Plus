-- Script to generate csv files for import into neo4j
-- This is the affymetrix case study tracing the affy seedset of <= 1991 to the Amplichip CYP450 
-- Panel of <= 2017 based on keyword searches in PubMed
-- Author: George Chacko 3/27/2018

-- End point is the garfield_hgraph series, which contains 23 wos_ids from Garfield's microarray historiograph
-- Starting point is all papers identified in a keyword search in PubMed for Amplichip CYP450
-- Publications are connected/related by citation. The target is cited by the source. Two generations each of cited and citing references from 
-- start and endpoints respectively are included in this network

-- Citation endpoint is 23 pubs in the garfield_historiograph (we restrict further by publication year)
DROP TABLE IF EXISTS garfield_hgraph_end;
CREATE TABLE garfield_hgraph_end AS
SELECT source_id, publication_year 
FROM wos_publications WHERE source_id IN 
(select distinct wos_id from garfield_hgraph2) AND
publication_year <= 1992;

-- get first gen of citing references (note target:cited_source_uid polarity to preserve a cites b)
-- the 9 endrefs are cited by gen1 pubs

DROP TABLE IF EXISTS garfield_gen1;
CREATE TABLE garfield_gen1 AS
SELECT source_id AS source, cited_source_uid AS target,
'source'::varchar(10) AS stype, 'endref'::varchar(10) AS ttype
FROM wos_references WHERE cited_source_uid IN
(select source_id from garfield_hgraph_end);
CREATE INDEX garfield_gen1_idx ON garfield_gen1(source);

-- get second gen of citing references
DROP TABLE IF EXISTS garfield_gen2;
CREATE TABLE garfield_gen2 AS
SELECT source_id AS source, cited_source_uid AS target,
'source'::varchar(10) AS stype, 'target'::varchar(10) AS ttype
FROM wos_references WHERE cited_source_uid IN
(select source from garfield_gen1);
CREATE INDEX garfield_gen2_idx ON garfield_gen2(source);

-- load amplichip data

DROP TABLE IF EXISTS garfield_amplichip;
CREATE TABLE garfield_amplichip (pmid int);
\COPY garfield_amplichip FROM '~/ERNIE/Analysis/affymetrix/garfield_amplichip.csv' CSV HEADER DELIMITER ','; 

DROP TABLE IF EXISTS garfield_amplichip2;
CREATE TABLE garfield_amplichip2 AS
SELECT a.pmid,b.wos_id 
FROM garfield_amplichip a
INNER JOIN wos_pmid_mapping b ON
a.pmid=b.pmid_int;

--Citation starting point is publications Amplichip CYP450 keyword search
-- get two generations of cited references not reversed polarity since this is cited reference not citing
DROP TABLE IF EXISTS garfield_amplichip_begina;
CREATE TABLE garfield_amplichip_begina AS
SELECT source_id AS source, cited_source_uid AS target,
'startref'::varchar(10) AS stype, 'target'::varchar(10) AS ttype
FROM wos_references WHERE source_id IN 
(select wos_id from garfield_amplichip2);
CREATE INDEX garfield_amplichip_begina_idx ON garfield_amplichip_begina(target);

-- Inner join on wos_pubs to get only viable references (complete WoS Ids)
DROP TABLE IF EXISTS garfield_amplichip_begin;
CREATE TABLE garfield_amplichip_begin AS
SELECT a.* FROM garfield_amplichip_begina a INNER JOIN
wos_publications b ON a.target=b.source_id;
CREATE INDEX garfield_amplichip_begin_idx on garfield_amplichip_begina(target);

-- Get second generation of cited references
DROP TABLE IF EXISTS garfield_amplichip_twog_a;
CREATE TABLE garfield_amplichip_twog_a AS
SELECT a.target AS source, 'source'::varchar(10) AS stype, b.cited_source_uid as target,'target'::varchar(10) as ttype
FROM garfield_amplichip_begin a INNER JOIN wos_references b ON a.target=b.source_id;

-- Inner join on wos_pubs to get only viable references (complete WoS Ids)
DROP TABLE IF EXISTS garfield_amplichip_twog;
CREATE TABLE garfield_amplichip_twog AS
SELECT a.* FROM garfield_amplichip_twog_a a INNER JOIN
wos_publications b ON a.target=b.source_id;

-- begin node list assembly process.
DROP TABLE IF EXISTS garfield_amplichip_node_assembly;
CREATE TABLE  garfield_amplichip_node_assembly(node_id varchar(16),
node_name varchar(19),stype varchar(10),ttype varchar(10));

--build node_table
-- insert from end point 
--gen1
INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,stype) 
SELECT DISTINCT 'n'||substring(source,5),source,stype
FROM garfield_gen1;

INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,ttype) 
SELECT DISTINCT 'n'||substring(target,5),target,ttype
FROM garfield_gen1;

--gen2
INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,stype) 
SELECT DISTINCT 'n'||substring(source,5),source,stype
FROM garfield_gen2;

INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,ttype) 
SELECT DISTINCT 'n'||substring(target,5),target,ttype
FROM garfield_gen2;

-- insert from start point (amplichip cyp450)
-- garfield_amplichip_begin
INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,stype) 
SELECT DISTINCT 'n'||substring(source,5),source,stype
FROM garfield_amplichip_begin;

INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,ttype) 
SELECT DISTINCT 'n'||substring(target,5),target,ttype
FROM garfield_amplichip_begin;

-- gen1_cited
INSERT INTO garfield_node_assembly(node_id,node_name,stype) 
SELECT DISTINCT 'n'||substring(source,5),source,stype
FROM garfield_amplichip_twog;

INSERT INTO garfield_amplichip_node_assembly(node_id,node_name,ttype) 
SELECT DISTINCT 'n'||substring(target,5),target,ttype
FROM garfield_amplichip_twog;
CREATE INDEX garfield_amplichip_node_assembly_idx ON garfield_amplichip_node_assembly(node_id);

DROP TABLE IF EXISTS garfield_amplichip_nodelist;
CREATE TABLE garfield_amplichip_nodelist AS
SELECT DISTINCT * FROM garfield_amplichip_node_assembly;

--build edge_table
DROP TABLE IF EXISTS garfield_amplichip_edge_table;
CREATE TABLE garfield_amplichip_edge_table(snid varchar(19), tnid varchar(19), source varchar(19), target varchar(19),
stype varchar(10),ttype varchar(10));

INSERT INTO garfield_amplichip_edge_table SELECT 'n'||substring(source,5) AS snid,
'n'||substring(target,5) as tnid, source, target, stype, ttype
FROM garfield_gen1;

INSERT INTO garfield_amplichip_edge_table SELECT 'n'||substring(source,5) AS snid,
'n'||substring(target,5) as tnid, source, target, stype, ttype
FROM garfield_gen2;

INSERT INTO garfield_amplichip_edge_table SELECT 'n'||substring(source,5) AS snid,
'n'||substring(target,5) as tnid, source, target, stype, ttype
FROM garfield_amplichip_begin;

INSERT INTO garfield_amplichip_edge_table SELECT 'n'||substring(source,5) AS snid,
'n'||substring(target,5) as tnid, source, target, stype, ttype
FROM garfield_amplichip_twog;
CREATE INDEX garfield_amplichip_edge_table_idx ON garfield_amplichip_edge_table(snid,tnid);

DROP TABLE IF EXISTS garfield_amplichip_edgelist;
CREATE TABLE garfield_amplichip_edgelist AS
SELECT DISTINCT * FROM garfield_amplichip_edge_table
ORDER BY snid,tnid;
CREATE INDEX garfield_amplichip_edgelist_idx ON garfield_amplichip_edgelist(source,target);

-- create formatted nodelist with unique node_ids
DROP TABLE IF EXISTS garfield_amplichip_nodelist_formatted_a;
CREATE TABLE garfield_amplichip_nodelist_formatted_a (node_id varchar(16), node_name varchar(19), 
stype varchar(10), ttype varchar(10), 
startref varchar(10), endref varchar(10));
INSERT INTO garfield_amplichip_nodelist_formatted_a (node_id,node_name,stype,ttype) 
SELECT DISTINCT * FROM garfield_amplichip_nodelist;			   

UPDATE garfield_amplichip_nodelist_formatted_a SET startref=1 WHERE stype='startref';
UPDATE garfield_amplichip_nodelist_formatted_a SET startref=0 WHERE stype='source' OR stype IS NULL;
UPDATE garfield_amplichip_nodelist_formatted_a SET endref=1 WHERE ttype='endref';
UPDATE garfield_amplichip_nodelist_formatted_a SET endref=0 WHERE ttype='target' OR ttype IS NULL;

DROP TABLE IF EXISTS garfield_amplichip_nodelist_formatted_b;
CREATE TABLE garfield_amplichip_nodelist_formatted_b AS
SELECT DISTINCT node_id, node_name, startref, endref FROM garfield_amplichip_nodelist_formatted_a;
CREATE INDEX garfield_amplichip_nodelist_formatted_b_idx ON garfield_amplichip_nodelist_formatted_b(node_name);

DROP TABLE IF EXISTS garfield_amplichip_nodelist_formatted_b_pmid;
CREATE TABLE garfield_amplichip_nodelist_formatted_b_pmid AS
SELECT a.*,b.pmid_int FROM garfield_amplichip_nodelist_formatted_b a 
LEFT JOIN wos_pmid_mapping b ON a.node_name=b.wos_id;

DROP TABLE IF EXISTS garfield_amplichip_nodelist_formatted_b_pmid_grants;
CREATE TABLE garfield_amplichip_nodelist_formatted_b_pmid_grants AS
SELECT
  a.*,
  EXISTS(SELECT 1
         FROM exporter_publink b
         WHERE a.pmid_int = b.pmid :: INT AND substring(b.project_number, 4, 2) = 'DA') AS nida_support,
  EXISTS(SELECT 1
         FROM exporter_publink b
         WHERE a.pmid_int = b.pmid :: INT AND substring(b.project_number, 4, 2) <> 'DA') AS other_hhs_support
FROM chackoge.garfield_amplichip_nodelist_formatted_b_pmid a;

DROP TABLE IF EXISTS garfield_amplichip_nodelist_formatted_c_pmid_grants;
CREATE TABLE garfield_amplichip_nodelist_formatted_c_pmid_grants AS
SELECT DISTINCT a.*,b.publication_year FROM garfield_amplichip_nodelist_formatted_b_pmid_grants a
LEFT JOIN wos_publications b ON a.node_name=b.source_id;

DROP TABLE IF EXISTS garfield_amplichip_nodelist_final;
CREATE TABLE garfield_amplichip_nodelist_final AS
SELECT DISTINCT node_id, node_name, startref, endref, nida_support, other_hhs_support, publication_year 
FROM garfield_amplichip_nodelist_formatted_c_pmid_grants;
CREATE INDEX garfield_amplichip_nodelist_final_idx ON garfield_amplichip_nodelist_final(node_name);

-- remove duplicate rows
DELETE FROM garfield_amplichip_nodelist_final WHERE node_id IN (select node_id from garfield_amplichip_nodelist_final ou
where (select count(*) from garfield_amplichip_nodelist_final inr
where inr.node_name = ou.node_name) > 1 order by node_name) AND startref='0' AND endref='0';

DELETE FROM garfield_amplichip_edgelist ou WHERE (select count(*) from garfield_amplichip_edgelist inr
where inr.source= ou.source and inr.target=ou.target) > 1 
AND stype='source' AND ttype='target';

-- adding a citation count column to nodelist

DROP TABLE IF EXISTS garfield_amplichip_node_citation_a;
CREATE TABLE garfield_amplichip_node_citation_a AS 
SELECT a.node_name,count(b.source_id) AS total_citation_count 
FROM garfield_amplichip_nodelist_final a LEFT JOIN wos_references b 
ON  a.node_name=b.cited_source_uid group by a.node_name;

DROP TABLE IF EXISTS garfield_amplichip_nodelist_final_citation;
CREATE TABLE garfield_amplichip_nodelist_final_citation AS
SELECT DISTINCT a.*,b.total_citation_count 
FROM garfield_amplichip_nodelist_final a 
LEFT JOIN garfield_node_citation_a b 
ON a.node_name=b.node_name;

-- copy tables to /tmp for import
COPY (
  SELECT node_name AS "wos_id:ID",
    CAST(startref = '1' AS text) AS "startref:boolean",
    CAST(endref = '1' AS text) AS "endref:boolean",
    CAST(nida_support AS text) AS "nida_support:boolean",
    CAST(other_hhs_support AS text) AS "other_hhs_support:boolean",
    publication_year AS "publication_year:int",
    total_citation_count AS "total_citations:int"
  FROM chackoge.garfield_amplichip_nodelist_final_citation
) TO '/tmp/garfield_amplichip_nodelist_2g_final.csv' WITH (FORMAT CSV, HEADER);

COPY (
  SELECT source AS ":START_ID",
    target AS ":END_ID"
  FROM chackoge.garfield_amplichip_edgelist
) TO '/tmp/garfield_amplichip_edgelist_2g_final.csv' WITH (FORMAT CSV, HEADER);


