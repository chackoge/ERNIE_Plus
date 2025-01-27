\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

CREATE OR REPLACE FUNCTION trg_load_open_citation_pub() RETURNS TRIGGER
  LANGUAGE plpgsql --
AS
$block$
BEGIN
  IF (tg_op = 'INSERT') THEN
    INSERT INTO open_citation_pubs(omid, title, authors, issue, volume, venue, pages, pub_year, pub_month,
                                   pub_date, type, publisher, editors)
    VALUES (split_part(new.id, ' ', 1),
      -- TODO change to in the future version:
      -- ltrim(split_part(new.id, ' ', 1), 'omid:')
            new.title, new.author, new.issue, new.volume, new.venue, new.page, extract_year(new.pub_date),
            extract_month(new.pub_date), to_date(new.pub_date), new.type, new.publisher, new.editor)
    ON CONFLICT(omid) DO NOTHING;

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

DROP TRIGGER IF EXISTS stg_open_citation_pubs_trg ON stg_open_citation_pubs;
CREATE TRIGGER stg_open_citation_pubs_trg
  INSTEAD OF INSERT
  ON stg_open_citation_pubs
  FOR EACH ROW
EXECUTE FUNCTION trg_load_open_citation_pub();