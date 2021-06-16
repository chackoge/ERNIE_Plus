CREATE TABLE cr_publications (
  doi VARCHAR(400)
    CONSTRAINT cr_publications_pk PRIMARY KEY USING INDEX TABLESPACE index_tbs,
  volume VARCHAR(40),
  pages VARCHAR(80),
  issn CHAR(9),
  deposited_date DATE,
  published_year SMALLINT
);

CREATE INDEX IF NOT EXISTS cp_published_year_i ON cr_publications(published_year) TABLESPACE index_tbs;

CREATE INDEX IF NOT EXISTS cp_issn_i ON cr_publications(issn) TABLESPACE index_tbs;

CREATE TABLE open_citations (
  oci VARCHAR(400)
    CONSTRAINT open_citations_pk PRIMARY KEY USING INDEX TABLESPACE index_tbs,
  citing VARCHAR(400),
  cited VARCHAR(400),
  creation_date DATE,
  time_span INTERVAL,
  citing_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date) ) STORED,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM creation_date - time_span) ) STORED
);

CREATE INDEX IF NOT EXISTS oc_citing_i ON open_citations(citing) TABLESPACE index_tbs;

CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations(cited) TABLESPACE index_tbs;

COMMENT ON COLUMN open_citations.creation_date IS --
  'The date on which the citation was created. This has the same value as the publication date of the citing
bibliographic resource, but is a property of the citation itself. Missing months in source data are defaulted to June
and missing days are defaulted to 15.';

COMMENT ON COLUMN open_citations.time_span IS --
  'The time span of a citation, i.e. the interval between the publication of the citing entity and the publication
of the cited entity.';

CREATE TABLE cr_pub_authors (
  doi VARCHAR(400),
  given_name VARCHAR(200),
  family_name VARCHAR(400),
  CONSTRAINT cr_pub_authors_pk PRIMARY KEY (doi, family_name, given_name) USING INDEX TABLESPACE index_tbs
);

CREATE INDEX IF NOT EXISTS cpa_family_name_given_name_i ON cr_pub_authors(family_name, given_name) TABLESPACE index_tbs;