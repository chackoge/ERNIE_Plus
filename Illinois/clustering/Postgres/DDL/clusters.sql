DROP TABLE IF EXISTS clusters.exosome_1900_2010_clusters CASCADE;

CREATE TABLE clusters.exosome_1900_2010_clusters (
  clustering_version VARCHAR(100),
  cluster_no INTEGER,
  min_k SMALLINT,
  modularity DOUBLE PRECISION,
  mcd INTEGER,
  cced DOUBLE PRECISION,
  CONSTRAINT exosome_1900_2010_clusters_pk
    PRIMARY KEY (clustering_version, cluster_no)
)
TABLESPACE clustering_tbs;

DROP TABLE IF EXISTS clusters.exosome_1900_2010_cluster_nodes CASCADE;

CREATE TABLE clusters.exosome_1900_2010_cluster_nodes (
  clustering_version VARCHAR(100),
  cluster_no INTEGER,
  node_seq_id INTEGER,
  is_core BOOLEAN,
  CONSTRAINT exosome_1900_2010_cluster_nodes_pk
    PRIMARY KEY (clustering_version, cluster_no, node_seq_id),
  CONSTRAINT e12cn_exosome_1900_2010_clusters_fk
    FOREIGN KEY (clustering_version, cluster_no)
      REFERENCES clusters.exosome_1900_2010_clusters --
      ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED
)
TABLESPACE clustering_tbs;

DROP TYPE IF EXISTS CORE_CLASSIFIER CASCADE;

CREATE TYPE CORE_CLASSIFIER AS ENUM ('Core', 'Non-Core');

DROP TABLE IF EXISTS clusters.stg_clusters CASCADE;

CREATE TABLE clusters.stg_clusters (
  cluster_no INTEGER,
  node_seq_id INTEGER,
  min_k SMALLINT,
  cluster_modularity DOUBLE PRECISION,
  mcd INTEGER,
  cced DOUBLE PRECISION,
  core_classifier CORE_CLASSIFIER
)
TABLESPACE clustering_tbs;

CREATE TABLE clusters.clustering_marker_nodes (
  marking_version VARCHAR(100),
  node_seq_id INTEGER,
  CONSTRAINT marker_nodes_pk
    PRIMARY KEY (marking_version, node_seq_id)
)
TABLESPACE clustering_tbs;

CREATE TABLE clusters.stg_marker_nodes (
  row_id INTEGER,
  node_seq_id INTEGER
)
TABLESPACE clustering_tbs;

