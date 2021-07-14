\set ON_ERROR_STOP on
\set ECHO all

CREATE TABLE IF NOT EXISTS dimensions.exosome_1900_1989_expanded (
    citing TEXT,
    cited TEXT,
    citing_id TEXT NOT NULL,
    cited_id TEXT NOT NULL,
    citing_year INTEGER,
    cited_year INTEGER,
    network_type text NOT NULL
);

COMMENT ON COLUMN dimensions.exosome_1900_1989_expanded.network_type IS 'Possible values are s_cited, s_citing, s_cited_cited, citing_s_cited, citing_s_citing, and citing_citing_s_cited';
