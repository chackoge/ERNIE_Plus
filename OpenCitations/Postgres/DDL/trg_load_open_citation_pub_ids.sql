\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

CREATE OR REPLACE FUNCTION trg_load_open_citation_pub_ids() RETURNS TRIGGER
  LANGUAGE plpgsql --
AS
$block$
BEGIN
  IF (tg_op = 'INSERT') THEN
    INSERT INTO open_citation_pub_ids(omid, id)
    SELECT 'omid:' || new.omid, st.item
    FROM string_to_table(new.id, ' ') AS st(item)
    ON CONFLICT(omid, id) DO NOTHING;

    /*
    A nonnull return value is used to signal that the trigger performed the necessary data modifications in the view.
    This will cause the count of the number of rows affected by the command to be incremented.
    */
    IF NOT found THEN
      RETURN NULL;
    END IF;

    RETURN new;
  END IF;

  RAISE 'Operation % is not supported', tg_op;
END;
$block$;

DROP TRIGGER IF EXISTS stg_open_citation_pub_ids_trg ON stg_open_citation_pub_ids;
CREATE TRIGGER stg_open_citation_pub_ids_trg
  INSTEAD OF INSERT
  ON stg_open_citation_pub_ids
  FOR EACH ROW
EXECUTE FUNCTION trg_load_open_citation_pub_ids();