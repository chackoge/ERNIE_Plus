/*
Postgres does not have the concept of "group" or "user" roles. The concept is implied through the use of a role
WITH LOGIN (user) and WITH NOLOGIN (group).
*/
CREATE ROLE developers WITH NOLOGIN;
GRANT developers TO :user;

ALTER TABLE :table OWNER TO developers;
ALTER MATERIALIZED VIEW :mv OWNER TO developers;
ALTER TABLE :table OWNER TO CURRENT_USER;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO PUBLIC;

GRANT ALL ON ALL TABLES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jenkins;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO jenkins;
GRANT ALL ON TABLESPACE :tablespace TO jenkins;

GRANT SELECT ON public.:table_name TO PUBLIC;

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- List grants on a table of a view
SELECT *
  FROM information_schema.role_table_grants
 WHERE table_schema = 'public' AND table_name = :table_name
 ORDER BY grantee;

-- List table grants ny grantee and privilege
SELECT grantee, privilege_type, string_agg(table_name, ', ') AS tables
  FROM information_schema.role_table_grants
 WHERE table_schema = 'public'
 GROUP BY grantee, privilege_type
 ORDER BY grantee, privilege_type;

-- List sequence grants ny grantee and privilege
SELECT grantee, privilege_type, string_agg(object_name, ', ') AS objects
-- SELECT grantee, privilege_type, string_agg(object_schema || '.' || object_name, ', ') AS objects
  FROM information_schema.role_usage_grants rug
 WHERE object_schema = 'public'
 GROUP BY grantee, privilege_type
 ORDER BY grantee, privilege_type;

-- List SP/UDF grants ny grantee and privilege
SELECT grantee, privilege_type, string_agg(routine_name, ', ') AS routines
-- SELECT grantee, privilege_type, string_agg(object_schema || '.' || object_name, ', ') AS objects
  FROM information_schema.role_routine_grants rrg
 WHERE routine_schema = 'public'
 GROUP BY grantee, privilege_type
 ORDER BY grantee, privilege_type;

-- List objects in a public schema without PUBLIC SELECT
SELECT table_name, table_type, pa.rolname AS owner
  FROM
    information_schema.tables t
      JOIN pg_class table_pc ON table_pc.relname = t.table_name
      JOIN pg_namespace pn ON pn.oid = table_pc.relnamespace AND pn.nspname = 'public'
      JOIN pg_authid pa ON pa.oid = table_pc.relowner
 WHERE t.table_schema = 'public' AND NOT has_table_privilege('public', table_pc.oid, 'SELECT')
 ORDER BY table_name;

-- Roles of a user
SELECT rolname
  FROM
    pg_user
      JOIN pg_auth_members ON (pg_user.usesysid = pg_auth_members.member)
      JOIN pg_roles ON (pg_roles.oid = pg_auth_members.roleid)
 WHERE pg_user.usename = :'user';