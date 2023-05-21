\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

CREATE TABLE open_citations (
  oci VARCHAR(1000)
    CONSTRAINT open_citations_pk
      PRIMARY KEY USING INDEX TABLESPACE open_citations_tbs,
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED
) TABLESPACE open_citations_tbs;

CREATE UNIQUE INDEX IF NOT EXISTS open_citations_uk ON open_citations (citing, cited) TABLESPACE open_citations_tbs;

CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations (cited) TABLESPACE open_citations_tbs;

--CREATE INDEX IF NOT EXISTS oc_citing_i ON open_citations(citing) TABLESPACE open_citations_tbs;

--CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations(cited) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citations IS --
  'Open Citations COCI: Crossref open DOI-to-DOI citations excluding duplicate, parallel, self and loop citations';

COMMENT ON COLUMN open_citations.citing IS --
  'DOI, lower-cased';

COMMENT ON COLUMN open_citations.cited IS --
  'DOI, lower-cased';

COMMENT ON COLUMN open_citations.creation_date IS --
  'The date on which the citation was created. This has the same value as the publication date of the citing
bibliographic resource but is a property of the citation itself. Missing months in source data default to June
and missing days default to 15.';

COMMENT ON COLUMN open_citations.time_span IS --
  'The time span of a citation, i.e. the interval between the publication of the citing entity and the publication
of the cited entity.';

COMMENT ON COLUMN open_citations.journal_sc IS --
  'Whether it is a journal self-citation (i.e. the citing and the cited entities are published in the same journal)';

COMMENT ON COLUMN open_citations.author_sc IS --
  'Whether it is an author self-citation (i.e. the citing and the cited entities have at least one author in common).';

ALTER TABLE open_citations
  OWNER TO devs;

CREATE TABLE open_citation_duplicates (
  oci VARCHAR(1000),
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED,
  CONSTRAINT open_citation_duplicates_pk
    PRIMARY KEY (oci, citing, cited, creation_date, time_span, journal_sc,
                 author_sc) USING INDEX TABLESPACE open_citations_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citation_duplicates IS 'Citations that duplicate an OCI in open_citations';

ALTER TABLE open_citation_duplicates
  OWNER TO devs;

CREATE TABLE open_citation_parallels (
  oci VARCHAR(1000),
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED,
  CONSTRAINT open_citation_parallels_pk
    PRIMARY KEY (oci) USING INDEX TABLESPACE open_citations_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citation_parallels IS 'Citations that parallel (citing -> cited) in open_citations';

ALTER TABLE open_citation_parallels
  OWNER TO devs;

CREATE TABLE open_citation_self (
  oci VARCHAR(1000),
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED,
  CONSTRAINT open_citation_self_pk
    PRIMARY KEY (oci) USING INDEX TABLESPACE open_citations_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citation_self IS 'Citations with citing = cited';

ALTER TABLE open_citation_self
  OWNER TO devs;

CREATE TABLE open_citation_loops (
  oci VARCHAR(1000),
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED,
  CONSTRAINT open_citation_loops_pk
    PRIMARY KEY (oci) USING INDEX TABLESPACE open_citations_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citation_loops IS 'Citations that loop back (cited -> citing) in open_citations';

ALTER TABLE open_citation_loops
  OWNER TO devs;

CREATE OR REPLACE VIEW stg_open_citations AS
SELECT oci, citing, cited, 'foo' AS creation, 'bar' AS timespan, journal_sc, author_sc, 'baz' AS source
FROM open_citations;

\include_relative trg_transform_and_load_open_citation.sql

CREATE SEQUENCE open_citation_pubs_seq MINVALUE 0;

-- TBD Refactor to a MATERIALIZED VIEW: some weird disk space errors were preventing that.
CREATE MATERIALIZED VIEW open_citation_pubs
  --CREATE TABLE open_citation_pubs
  TABLESPACE open_citations_tbs AS
SELECT sq.doi, nextval('open_citation_pubs_seq') AS iid
FROM (
       SELECT citing AS doi
       FROM open_citations
       UNION
       -- DISTINCT values only
       SELECT cited
       FROM open_citations
     ) sq
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW open_citation_pubs IS ---
  'Unique publications with original DOIs extracted from open_citations';

/*
ALTER TABLE open_citation_pubs
  ADD CONSTRAINT open_citation_pubs_pk
    PRIMARY KEY (doi) USING INDEX TABLESPACE open_citations_tbs;
-- 1m:01s–4m:02s
*/

CREATE UNIQUE INDEX IF NOT EXISTS open_citations_pubs_uk ON open_citation_pubs (iid) --
  TABLESPACE open_citations_tbs;
-- 20s

ALTER MATERIALIZED VIEW open_citation_pubs
  OWNER TO devs;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;

GRANT ALL ON ALL TABLES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO jenkins;
