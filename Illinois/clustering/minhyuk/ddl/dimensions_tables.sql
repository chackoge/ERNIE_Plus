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
  cited_integer_id INTEGER,
  CONSTRAINT exosome_1900_2010_sabpq_deduplicated_pk PRIMARY KEY (citing_integer_id, cited_integer_id)
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_2010_sabpq_deduplicated_top_10_pruned (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER,
  citing_integer_id INTEGER,
  cited_integer_id INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_2010_sabpq_deduplicated_top_100_pruned (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER,
  citing_integer_id INTEGER,
  cited_integer_id INTEGER
);

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_2010_sabpq_deleted_edges ( -- these edges were deleted since they created loops (e.g. 3->4 and 4->3)
    citing TEXT,
    cited TEXT,
    citing_id TEXT NOT NULL,
    cited_id TEXT NOT NULL,
    citing_year INTEGER,
    cited_year INTEGER,
    citing_integer_id INTEGER,
    cited_integer_id INTEGER
);

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

CREATE TABLE IF NOT EXISTS dimensions.blast_sabpq_edgelist (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER,
  citing_integer_id INTEGER,
  cited_integer_id INTEGER,
  CONSTRAINT blast_sabpq_deduplicated_pk PRIMARY KEY (citing_integer_id, cited_integer_id)
);

CREATE TABLE IF NOT EXISTS dimensions.blast_sabpq_nodelist (
    node_id TEXT,
    integer_id INTEGER -- this is a series starting at 0
);

CREATE TABLE IF NOT EXISTS dimensions.blast_sabpq_deleted_edges ( -- these edges were deleted since they created loops (e.g. 3->4 and 4->3)
    citing TEXT,
    cited TEXT,
    citing_id TEXT NOT NULL,
    cited_id TEXT NOT NULL,
    citing_year INTEGER,
    cited_year INTEGER,
    citing_integer_id INTEGER,
    cited_integer_id INTEGER
);
