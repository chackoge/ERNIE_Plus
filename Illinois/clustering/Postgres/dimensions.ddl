DROP TABLE IF EXISTS dimensions.exosome_1900_2010_clusters CASCADE;

CREATE TABLE dimensions.exosome_1900_2010_clusters (
  clustering_version VARCHAR(100),
  cluster_no INTEGER,
  min_k SMALLINT,
  cluster_modularity DOUBLE PRECISION,
  CONSTRAINT exosome_1900_2010_clusters_pk
    PRIMARY KEY (clustering_version, cluster_no)
)
TABLESPACE clustering_tbs;

DROP TABLE IF EXISTS dimensions.exosome_1900_2010_cluster_nodes CASCADE;

CREATE TABLE dimensions.exosome_1900_2010_cluster_nodes (
  clustering_version VARCHAR(100),
  cluster_no INTEGER,
  node_seq_id INTEGER,
  CONSTRAINT exosome_1900_2010_cluster_nodes_pk
    PRIMARY KEY (clustering_version, cluster_no, node_seq_id),
  CONSTRAINT e12cn_exosome_1900_2010_clusters_fk
    FOREIGN KEY (clustering_version, cluster_no)
      REFERENCES dimensions.exosome_1900_2010_clusters --
      ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED
)
TABLESPACE clustering_tbs;

DROP TABLE IF EXISTS dimensions.stg_clusters CASCADE;

CREATE TABLE dimensions.stg_clusters (
  cluster_no INTEGER,
  min_k SMALLINT,
  cluster_modularity DOUBLE PRECISION,
  node_seq_id INTEGER
)
TABLESPACE clustering_tbs;

