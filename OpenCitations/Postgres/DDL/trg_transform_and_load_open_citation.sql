\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

CREATE OR REPLACE FUNCTION extract_year(date_string TEXT) --
  RETURNS SMALLINT
  /**
  Extracts year from YYYY[-MM][-DD] string
  */
RETURN cast(left(date_string, 4) AS SMALLINT);

CREATE OR REPLACE FUNCTION extract_month(date_string TEXT) --
  RETURNS SMALLINT
  /**
  Extracts month from YYYY[-MM][-DD] string
  */
RETURN cast(nullif(substr(date_string, 6, 2), '') AS SMALLINT);

CREATE OR REPLACE FUNCTION to_date(date_string TEXT) --
  RETURNS DATE
  /**
  Converts YYYY[-MM][-DD] string to a DATE
  @return NULL for incomplete dates
  */
RETURN CASE WHEN length(date_string) = length('YYYY-MM-DD') THEN to_date(date_string, 'YYYY-MM-DD') END;

CREATE OR REPLACE FUNCTION to_interval(signed_iso_8601_interval TEXT) --
  RETURNS INTERVAL
  /**
  Converts [-]P{quantity}{unit}[{quantity}{unit} ...] string to an INTERVAL
  */
RETURN CASE
         WHEN left(signed_iso_8601_interval, 1) = '-' THEN -cast(substr(signed_iso_8601_interval, 2) AS INTERVAL)
         ELSE cast(signed_iso_8601_interval AS INTERVAL)
       END;

CREATE OR REPLACE FUNCTION trg_transform_and_load_open_citation() --
  RETURNS TRIGGER
  LANGUAGE plpgsql --
AS
$block$
BEGIN
  IF (tg_op = 'INSERT') THEN
    IF lower(new.citing) = lower(new.cited) THEN
      INSERT INTO open_citations_self(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                      time_span, author_sc, journal_sc)
      VALUES
        (new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
         to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc)
      ON CONFLICT DO NOTHING;

      RETURN NULL;
    END IF;

    IF new.creation IS NULL OR extract_year(new.creation) > extract(YEAR FROM current_date) THEN
      INSERT INTO open_citations_no_valid_pub_date(oci, citing, cited, citing_pub_year, citing_pub_month,
                                                   citing_pub_date,
                                                   time_span, author_sc, journal_sc)
      VALUES
        (new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
         to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc)
      ON CONFLICT DO NOTHING;

      RETURN NULL;
    END IF;

    INSERT INTO open_citations_duplicate(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                         time_span, author_sc, journal_sc)
    SELECT new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
      to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc
    FROM open_citations oc
    WHERE
      oc.oci = new.oci
    ON CONFLICT(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date, time_span, author_sc, --
      journal_sc) DO UPDATE -- NOP, but DO UPDATE is needed to set FOUND
      SET
        oci = excluded.oci;
    IF found THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citations_looping(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                       time_span, author_sc, journal_sc)
    SELECT new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
      to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc
    FROM open_citations oc
    WHERE
      oc.citing = lower(new.cited)
      AND oc.cited = lower(new.citing)
    ON CONFLICT(oci) DO UPDATE -- NOP, but DO UPDATE is needed to set FOUND
      SET
        oci = excluded.oci;
    IF found THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citations_parallel(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                        time_span, author_sc, journal_sc)
    SELECT new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
      to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc
    FROM open_citations oc
    WHERE
      oc.citing = lower(new.citing)
      AND oc.cited = lower(new.cited)
    ON CONFLICT(oci) DO UPDATE -- NOP, but DO UPDATE is needed to set FOUND
      SET
        oci = excluded.oci;
    IF found THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citations(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                               time_span, author_sc, journal_sc)
    VALUES
      (new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
       to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc)
    ON CONFLICT(oci, citing_pub_year) DO NOTHING;
    IF NOT found THEN
      RETURN NULL;
    END IF;

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