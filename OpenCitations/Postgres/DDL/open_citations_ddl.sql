\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

CREATE TABLE open_citations (
  oci VARCHAR(1000),
  citing VARCHAR(400) NOT NULL,
  cited VARCHAR(400) NOT NULL,
  citing_pub_year SMALLINT,
  citing_pub_month SMALLINT,
  citing_pub_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM citing_pub_date - time_span) ) STORED,
  CONSTRAINT open_citations_pk PRIMARY KEY (oci, citing_pub_year) USING INDEX TABLESPACE index_tbs
) PARTITION BY RANGE (citing_pub_year) TABLESPACE open_citations_tbs;

-- Partitions
DO
$block$
  DECLARE
    year SMALLINT;
    century SMALLINT;
    sql TEXT;
  BEGIN
    FOR year IN 1900..extract(YEAR FROM current_date)
      LOOP
        sql := format('CREATE TABLE open_citations_%s PARTITION OF open_citations
                      FOR VALUES FROM (%1$s) TO (%1$s + 1)
                      TABLESPACE open_citations_tbs', year);
        RAISE NOTICE USING MESSAGE = sql || ';';
        EXECUTE sql;
      END LOOP;

    -- Citations start from publication year 1500
    FOR century IN 16..19
      LOOP
        sql := format('CREATE TABLE open_citations_%s_%s PARTITION OF open_citations
                      FOR VALUES FROM (%1$s) TO (%2$s + 1)
                      TABLESPACE open_citations_tbs', (century - 1) * 100, (century - 1) * 100 + 99);
        RAISE NOTICE USING MESSAGE = sql || ';';
        EXECUTE sql;
      END LOOP;
  END;
$block$;

CREATE UNIQUE INDEX IF NOT EXISTS open_citations_uk ON open_citations(citing, cited, citing_pub_year) --
  TABLESPACE index_tbs;

CREATE INDEX IF NOT EXISTS oc_cited_i ON open_citations(cited) TABLESPACE index_tbs;

COMMENT ON TABLE open_citations IS --
  'Open Citations COCI: Crossref open DOI-to-DOI citations excluding citation anomalies';

COMMENT ON COLUMN open_citations.citing IS --
  'DOI, lower-cased';

COMMENT ON COLUMN open_citations.cited IS --
  'DOI, lower-cased';

COMMENT ON COLUMN open_citations.citing_pub_year IS 'The publication year of the citing bibliographic resource';

COMMENT ON COLUMN open_citations.citing_pub_month IS 'The publication month of the citing bibliographic resource';

COMMENT ON COLUMN open_citations.citing_pub_date IS 'The publication date of the citing bibliographic resource';

COMMENT ON COLUMN open_citations.time_span IS --
  'The interval between the publications of the citing entity and the cited entity.';

COMMENT ON COLUMN open_citations.journal_sc IS --
  'Whether it is a journal self-citation (i.e. the citing and the cited entities are published in the same journal)';

COMMENT ON COLUMN open_citations.author_sc IS --
  'Whether it is an author self-citation (i.e. the citing and the cited entities have at least one author in common).';

ALTER TABLE open_citations
  OWNER TO devs;

CREATE TABLE open_citations_duplicate (
  oci VARCHAR(1000),
  citing VARCHAR(400) NOT NULL,
  cited VARCHAR(400) NOT NULL,
  citing_pub_year SMALLINT,
  citing_pub_month SMALLINT,
  citing_pub_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM citing_pub_date - time_span) ) STORED
) TABLESPACE open_citations_tbs;

CREATE UNIQUE INDEX IF NOT EXISTS open_citations_duplicate_uk --
  ON open_citations_duplicate(oci, citing, cited,
                              citing_pub_year,
                              citing_pub_month,
                              citing_pub_date, time_span,
                              journal_sc,
                              author_sc) TABLESPACE index_tbs;

COMMENT ON TABLE open_citations_duplicate IS --
  'Citations with a duplicate OCI to `open_citations` but different data in an other column';

ALTER TABLE open_citations_duplicate
  OWNER TO devs;

CREATE TABLE open_citations_parallel (
  oci VARCHAR(1000),
  citing VARCHAR(400) NOT NULL,
  cited VARCHAR(400) NOT NULL,
  citing_pub_year SMALLINT,
  citing_pub_month SMALLINT,
  citing_pub_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM citing_pub_date - time_span) ) STORED,
  CONSTRAINT open_citations_parallel_pk PRIMARY KEY (oci) USING INDEX TABLESPACE index_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citations_parallel IS 'Citations that parallel (citing -> cited) in `open_citations`';

ALTER TABLE open_citations_parallel
  OWNER TO devs;

CREATE TABLE open_citations_self (
  oci VARCHAR(1000),
  citing VARCHAR(400) NOT NULL,
  cited VARCHAR(400) NOT NULL,
  citing_pub_year SMALLINT,
  citing_pub_month SMALLINT,
  citing_pub_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM citing_pub_date - time_span) ) STORED,
  CONSTRAINT open_citations_self_pk PRIMARY KEY (oci) USING INDEX TABLESPACE index_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citations_self IS 'Citations with citing = cited';

ALTER TABLE open_citations_self
  OWNER TO devs;

CREATE TABLE open_citations_looping (
  oci VARCHAR(1000),
  citing VARCHAR(400) NOT NULL,
  cited VARCHAR(400) NOT NULL,
  citing_pub_year SMALLINT,
  citing_pub_month SMALLINT,
  citing_pub_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM citing_pub_date - time_span) ) STORED,
  CONSTRAINT open_citations_looping_pk PRIMARY KEY (oci) USING INDEX TABLESPACE index_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citations_looping IS 'Citations that loop back (cited -> citing) comparing with `open_citations`';

ALTER TABLE open_citations_looping
  OWNER TO devs;

CREATE TABLE open_citations_no_valid_pub_date (
  oci VARCHAR(1000),
  citing VARCHAR(400) NOT NULL,
  cited VARCHAR(400) NOT NULL,
  citing_pub_year SMALLINT,
  citing_pub_month SMALLINT,
  citing_pub_date DATE,
  time_span INTERVAL,
  journal_sc BOOLEAN,
  author_sc BOOLEAN,
  cited_pub_year SMALLINT GENERATED ALWAYS AS ( extract(YEAR FROM citing_pub_date - time_span) ) STORED,
  CONSTRAINT open_citations_future_pk PRIMARY KEY (oci) USING INDEX TABLESPACE index_tbs
) TABLESPACE open_citations_tbs;

COMMENT ON TABLE open_citations_no_valid_pub_date IS --
  'Citations with either unknown pub date or the future publication year';

ALTER TABLE open_citations_no_valid_pub_date
  OWNER TO devs;

CREATE OR REPLACE VIEW stg_open_citations AS
SELECT oci, citing, cited, 'foo' AS creation, 'bar' AS timespan, journal_sc, author_sc
FROM open_citations;

\include_relative trg_transform_and_load_open_citation.sql

DROP SEQUENCE IF EXISTS open_citation_pubs_seq;
CREATE SEQUENCE open_citation_pubs_seq MINVALUE 0;
ALTER SEQUENCE open_citation_pubs_seq OWNER TO devs;

CREATE MATERIALIZED VIEW open_citation_pubs TABLESPACE open_citations_tbs AS
SELECT sq.doi, nextval('open_citation_pubs_seq') AS iid
FROM (SELECT citing AS doi
      FROM open_citations
      UNION
      -- DISTINCT values only
      SELECT cited
      FROM open_citations) sq
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW open_citation_pubs IS ---
  'Unique publications with original DOIs extracted from open_citations';

CREATE UNIQUE INDEX IF NOT EXISTS open_citation_pubs_doi_uk ON open_citation_pubs(doi) --
  TABLESPACE index_tbs;

CREATE UNIQUE INDEX IF NOT EXISTS open_citation_pubs_iid_uk ON open_citation_pubs(iid) --
  TABLESPACE index_tbs;

ALTER MATERIALIZED VIEW open_citation_pubs OWNER TO devs;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;
GRANT pg_read_server_files TO devs;

GRANT ALL ON ALL TABLES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO jenkins;
GRANT CREATE ON SCHEMA public TO jenkins;