\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

CREATE OR REPLACE FUNCTION to_date(date_string TEXT) --
  RETURNS DATE
  /**
  Converts YYYY[-MM][-DD] string to a DATE
  @return default omitted month to June and omitted day to 15
  */
RETURN make_date(cast(left(date_string, 4) AS INT), --
                 cast(coalesce(nullif(substr(date_string, 6, 2), ''), '6') AS INT),
                 cast(coalesce(nullif(substr(date_string, 9), ''), '15') AS INT));

CREATE OR REPLACE FUNCTION to_interval(signed_iso_8601_interval TEXT) --
  RETURNS INTERVAL
  /**
  Converts [-]P{quantity}{unit}[{quantity}{unit} ...] string to an INTERVAL
  */
RETURN CASE
         WHEN left(signed_iso_8601_interval, 1) = '-' THEN -cast(substr(signed_iso_8601_interval, 2) AS INTERVAL)
         ELSE cast(signed_iso_8601_interval AS INTERVAL)
       END;

-- trg_transform_and_load_open_citation(): routine
CREATE OR REPLACE FUNCTION trg_transform_and_load_open_citation() --
  RETURNS TRIGGER
  LANGUAGE plpgsql --
AS
$block$
BEGIN
  IF (tg_op = 'INSERT') THEN
    INSERT INTO open_citation_self(oci, citing, cited, creation_date, time_span, author_sc, journal_sc)
    SELECT new.oci,
           new.citing,
           new.cited,
           to_date(new.creation),
           to_interval(new.timespan),
           new.author_sc,
           new.journal_sc
    FROM open_citations oc
    WHERE lower(new.citing) = lower(new.cited);
    IF FOUND THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citation_duplicates(oci, citing, cited, creation_date, time_span, author_sc, journal_sc)
    SELECT new.oci,
           new.citing,
           new.cited,
           to_date(new.creation),
           to_interval(new.timespan),
           new.author_sc,
           new.journal_sc
    FROM open_citations oc
    WHERE oc.oci = new.oci;
    IF FOUND THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citation_parallels(oci, citing, cited, creation_date, time_span, author_sc, journal_sc)
    SELECT new.oci,
           new.citing,
           new.cited,
           to_date(new.creation),
           to_interval(new.timespan),
           new.author_sc,
           new.journal_sc
    FROM open_citations oc
    WHERE oc.citing = lower(new.citing)
      AND oc.cited = lower(new.cited);
    IF FOUND THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citation_loops(oci, citing, cited, creation_date, time_span, author_sc, journal_sc)
    SELECT new.oci,
           new.citing,
           new.cited,
           to_date(new.creation),
           to_interval(new.timespan),
           new.author_sc,
           new.journal_sc
    FROM open_citations oc
    WHERE oc.citing = lower(new.cited)
      AND oc.cited = lower(new.citing);
    IF FOUND THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citations(oci, citing, cited, creation_date, time_span, author_sc, journal_sc)
    VALUES (new.oci,
            lower(new.citing),
            lower(new.cited),
            to_date(new.creation),
            to_interval(new.timespan),
            new.author_sc,
            new.journal_sc);
    /*
    A nonnull return value is used to signal that the trigger performed the necessary data modifications in the view.
    This will cause the count of the number of rows affected by the command to be incremented
    */
    RETURN new;
  END IF;
  RAISE 'Operation % is not supported', tg_op;
END;
$block$;

DROP TRIGGER IF EXISTS stg_open_citations_trg ON stg_open_citations;
CREATE TRIGGER stg_open_citations_trg
  INSTEAD OF INSERT
  ON stg_open_citations
  FOR EACH ROW
EXECUTE FUNCTION trg_transform_and_load_open_citation();