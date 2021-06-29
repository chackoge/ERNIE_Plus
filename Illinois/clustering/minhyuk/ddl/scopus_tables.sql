\set ON_ERROR_STOP on
\set ECHO all

CREATE TABLE IF NOT EXISTS scopus_europepmc_filepaths (
    doi TEXT NOT NULL,
    sgr BIGINT CONSTRAINT scopus_europepmc_filepaths_pk PRIMARY KEY,
    filepath TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scopus_europepmc_edgegraph (
    citing BIGINT NOT NULL,
    cited BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS scopus_europepmc_id_to_doi_backup (
    sgr BIGINT CONSTRAINT scopus_europepmc_id_to_doi_backup_pk PRIMARY KEY,
    doi TEXT NOT NULL
);
