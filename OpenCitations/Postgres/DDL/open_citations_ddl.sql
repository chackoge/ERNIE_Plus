\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

CREATE TABLE cr_publications (
  doi VARCHAR(400)
    CONSTRAINT cr_publications_pk
      PRIMARY KEY /*USING INDEX TABLESPACE index_tbs*/,
  volume VARCHAR(40),
  pages VARCHAR(80),
  issn CHAR(9),
  deposited_date DATE,
  published_year SMALLINT
);

CREATE INDEX IF NOT EXISTS cp_published_year_i ON cr_publications(published_year) /*TABLESPACE index_tbs*/;

CREATE INDEX IF NOT EXISTS cp_issn_i ON cr_publications(issn) /*TABLESPACE index_tbs*/;

CREATE TABLE cr_pub_authors (
  doi VARCHAR(400),
  given_name VARCHAR(200),
  family_name VARCHAR(400),
  CONSTRAINT cr_pub_authors_pk
    PRIMARY KEY (doi, family_name, given_name) --USING INDEX TABLESPACE index_tbs
);

CREATE INDEX IF NOT EXISTS cpa_family_name_given_name_i ON cr_pub_authors(family_name, given_name)
/*TABLESPACE index_tbs*/;

CREATE TABLE open_citations (
  oci VARCHAR(1000)
    CONSTRAINT open_citations_pk
      PRIMARY KEY USING INDEX TABLESPACE open_citations_tbs,
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED
)
TABLESPACE open_citations_tbs;

CREATE INDEX IF NOT EXISTS oc_citing_i ON open_citations(citing) TABLESPACE open_citations_tbs;

CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations(cited) TABLESPACE open_citations_tbs;

COMMENT ON COLUMN open_citations.creation_date IS --
  'The date on which the citation was created. This has the same value as the publication date of the citing
bibliographic resource but is a property of the citation itself. Missing months in source data default to June
and missing days default to 15.';

COMMENT ON COLUMN open_citations.time_span IS --
  'The time span of a citation, i.e. the interval between the publication of the citing entity and the publication
of the cited entity.';

ALTER TABLE open_citations
  OWNER TO developers;

CREATE OR REPLACE VIEW stg_open_citations AS
SELECT oci, citing, cited, 'foo' AS creation, 'bar' AS timespan, 'baz' AS journal_sc, 'qux' AS author_sc
  FROM open_citations;

\include_relative trg_transform_and_load_open_citation.sql

-- 32h:35m
-- TBD Refactor to a MATERIALIZED VIEW: some weird disk space errors were preventing that.
CREATE TABLE open_citations_invalid
TABLESPACE open_citations_tbs AS
SELECT *
  FROM open_citations oc
 WHERE
    -- Self-citations
   citing = cited
    OR
    -- Parallel edges
   EXISTS(SELECT 1 FROM open_citations oc2 WHERE oc2.citing = oc.citing AND oc2.cited = oc.cited AND oc2.oci <> oc.oci);

COMMENT ON TABLE open_citations_invalid IS ---
  'Self-citations and parallel edges';

ALTER TABLE open_citations_invalid
  ADD CONSTRAINT open_citations_invalid_pk
    PRIMARY KEY (oci) USING INDEX TABLESPACE open_citations_tbs;

CREATE SEQUENCE open_citation_pubs_seq MINVALUE 0;

-- TBD Refactor to a MATERIALIZED VIEW: some weird disk space errors were preventing that.
CREATE TABLE open_citation_pubs
TABLESPACE open_citations_tbs AS
SELECT sq.doi, nextval('open_citation_pubs_seq') AS iid
  FROM ( -- DOI case can be normalized, e.g. lower-cased, but this yields the same number of publications
    SELECT citing AS doi
      FROM open_citations
     UNION
-- DISTINCT values only
    SELECT cited
      FROM open_citations
  ) sq;

COMMENT ON TABLE open_citation_pubs IS ---
  'Unique publications with original DOIs extracted from open_citations';

-- 4m:02s
ALTER TABLE open_citation_pubs
  ADD CONSTRAINT open_citation_pubs_pk
    PRIMARY KEY (doi) USING INDEX TABLESPACE open_citations_tbs;

-- 20s
CREATE UNIQUE INDEX IF NOT EXISTS open_citations_pubs_uk ON open_citations_pubs(iid) --
  TABLESPACE open_citations_tbs;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;

GRANT ALL ON ALL TABLES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO jenkins;