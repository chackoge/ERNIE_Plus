CREATE TABLE dimensions.exosome_1900_2010_sabpq_nodelist (
  node_id TEXT NOT NULL
    CONSTRAINT exosome_1900_2010_sabpq_nodelist_pk
      PRIMARY KEY,
  in_degree BIGINT,
  out_degree BIGINT,
  integer_id SERIAL NOT NULL
);

CREATE INDEX IF NOT EXISTS d12sn_integer_id_i ON dimensions.exosome_1900_2010_sabpq_nodelist(integer_id);
-- 7s

ALTER TABLE dimensions.exosome_1900_2010_sabpq_nodelist
  OWNER TO chackoge;

CREATE TABLE exosome_1900_2010_sabpq_deduplicated (
  citing TEXT,
  cited TEXT,
  citing_id TEXT NOT NULL,
  cited_id TEXT NOT NULL,
  citing_year INTEGER,
  cited_year INTEGER,
  citing_integer_id INTEGER NOT NULL,
  cited_integer_id INTEGER NOT NULL,
  CONSTRAINT exosome_1900_2010_sabpq_deduplicated_pk
    PRIMARY KEY (citing_integer_id, cited_integer_id)
);

CREATE INDEX IF NOT EXISTS e12sd_cited_integer_id_i ON dimensions.exosome_1900_2010_sabpq_deduplicated(cited_integer_id);
-- 1m:40s

COMMENT ON COLUMN exosome_1900_2010_sabpq_deduplicated.citing_integer_id IS 'The integer id starts at 0 and is based on dimensions.exosome_1900_2010_sabpq_nodelist table';

COMMENT ON COLUMN exosome_1900_2010_sabpq_deduplicated.cited_integer_id IS 'The integer id starts at 0 and is based on dimensions.exosome_1900_2010_sabpq_nodelist table';

ALTER TABLE exosome_1900_2010_sabpq_deduplicated
  OWNER TO minhyuk2;

