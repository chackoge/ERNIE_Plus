\set ON_ERROR_STOP on
\set ECHO all

CREATE TABLE IF NOT EXISTS scopus_europepmc_results (
    doi TEXT NOT NULL,
    filepath TEXT NOT NULL
);
