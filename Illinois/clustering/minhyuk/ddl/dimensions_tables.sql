\set ON_ERROR_STOP on
\set ECHO all

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_1989_expanded (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER,
  network_type TEXT NOT NULL
);

COMMENT ON COLUMN dimensions.exosome_1900_1989_expanded.network_type IS 'Possible values are s_cited, s_citing, s_cited_cited, citing_s_cited, citing_s_citing, and citing_citing_s_cited';


CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_1989_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);


CREATE TABLE IF NOT EXISTS dimensions.exosome_1990_1997_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);


CREATE TABLE IF NOT EXISTS dimensions.exosome_1998_2004_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_2005_2009_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_2010_2012_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_2013_2014_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_2015_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_2016_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_2010_sabpq_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER,
  citing_integer_id INTEGER,
  cited_integer_id INTEGER
);

ALTER TABLE dimensions.exosome_1900_2010_sabpq_deduplicated
  ADD CONSTRAINT exosome_1900_2010_sabpq_deduplicated_pk
    PRIMARY KEY (citing_integer_id, cited_integer_id);

COMMENT ON COLUMN dimensions.exosome_1900_2010_sabpq_deduplicated.citing_integer_id IS 'The integer id starts at 0 and is based on dimensions.exosome_1900_2010_sabpq_nodelist table';
COMMENT ON COLUMN dimensions.exosome_1900_2010_sabpq_deduplicated.cited_integer_id IS 'The integer id starts at 0 and is based on dimensions.exosome_1900_2010_sabpq_nodelist table';

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_2010_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER
);
