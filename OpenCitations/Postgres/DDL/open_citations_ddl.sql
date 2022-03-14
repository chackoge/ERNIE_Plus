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
      PRIMARY KEY /*USING INDEX TABLESPACE index_tbs*/,
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED
) TABLESPACE open_citations_tbs;

CREATE INDEX IF NOT EXISTS oc_citing_i ON open_citations(citing) /*TABLESPACE index_tbs*/;

CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations(cited) /*TABLESPACE index_tbs*/;

COMMENT ON COLUMN open_citations.creation_date IS --
  'The date on which the citation was created. This has the same value as the publication date of the citing
bibliographic resource but is a property of the citation itself. Missing months in source data default to June
and missing days default to 15.';

COMMENT ON COLUMN open_citations.time_span IS --
  'The time span of a citation, i.e. the interval between the publication of the citing entity and the publication
of the cited entity.';

CREATE OR REPLACE VIEW stg_open_citations AS
SELECT oci, citing, cited, 'foo' AS creation, 'bar' AS timespan, 'baz' AS journal_sc, 'qux' AS author_sc
  FROM open_citations;

\include_relative trg_transform_and_load_open_citation.sql

DROP TRIGGER IF EXISTS stg_open_citations_trg ON stg_open_citations;
CREATE TRIGGER stg_open_citations_trg
  INSTEAD OF INSERT
  ON stg_open_citations
  FOR EACH ROW
EXECUTE FUNCTION trg_transform_and_load_open_citation();