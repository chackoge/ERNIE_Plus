-- Next sequence value
SELECT nextval(:'seq');

-- Last sequence value in the current session
SELECT currval(:'seq');

-- Set the counter (as if the last) value
SELECT setval(:'seq', :counter_value);

-- Get name of the sequence that a serial or identity column uses
SELECT pg_get_serial_sequence(:'table', :'column');

-- Sequence metadata
SELECT ps.*, pa.rolname AS owner
FROM pg_sequence ps
       JOIN pg_class AS pc
            ON (pc.oid = ps.seqrelid)
       JOIN pg_authid AS pa
            ON (pa.oid = pc.relowner);