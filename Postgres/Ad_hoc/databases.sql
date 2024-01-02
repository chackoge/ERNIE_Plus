-- Databases and their owners
SELECT pd.datname AS db, pa.rolname AS db_owner, pt.spcname AS default_tablespace
FROM pg_database AS pd
       JOIN pg_authid AS pa ON (pa.oid = pd.datdba)
       JOIN pg_tablespace pt ON (pt.oid = pd.dattablespace)
ORDER BY db;

SELECT current_database();

CREATE DATABASE root OWNER root;

ALTER DATABASE ${db} OWNER TO ${user};

DROP DATABASE ${db};