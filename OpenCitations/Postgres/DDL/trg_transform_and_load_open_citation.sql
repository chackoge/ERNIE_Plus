\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

CREATE OR REPLACE FUNCTION trg_transform_and_load_open_citation() RETURNS TRIGGER
  LANGUAGE plpgsql --
AS
$block$
BEGIN
  IF (tg_op = 'INSERT') THEN
    IF lower(new.citing) = lower(new.cited) THEN
      INSERT INTO open_citations_self(oci, citing,
                                      cited,
                                      citing_pub_year,
                                      citing_pub_month,
                                      citing_pub_date,
                                      time_span,
                                      author_sc,
                                      journal_sc)
      VALUES (new.oci, new.citing, new.cited,
              extract_year(new.creation),
              extract_month(new.creation),
              to_date(new.creation),
              to_interval(new.timespan),
              new.author_sc, new.journal_sc)
      ON CONFLICT(oci) DO NOTHING;

      RETURN NULL;
    END IF;

    IF new.creation IS NULL OR extract_year(new.creation) > extract(YEAR FROM current_date) THEN
      INSERT INTO open_citations_no_valid_dating(oci,
                                                 citing,
                                                 cited,
                                                 citing_pub_year,
                                                 citing_pub_month,
                                                 citing_pub_date,
                                                 time_span,
                                                 author_sc,
                                                 journal_sc)
      VALUES (new.oci, new.citing, new.cited,
              extract_year(new.creation),
              extract_month(new.creation),
              to_date(new.creation),
              to_interval(new.timespan), new.author_sc,
              new.journal_sc)
      ON CONFLICT(oci) DO NOTHING;

      RETURN NULL;
    END IF;

    INSERT INTO open_citations_duplicate(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                         time_span, author_sc, journal_sc)
    WITH cte AS (
      SELECT new.oci, new.citing, new.cited, extract_year(new.creation) AS citing_pub_year,
             extract_month(new.creation) AS citing_pub_month, to_date(new.creation) AS citing_pub_date,
             to_interval(new.timespan) AS time_span, new.author_sc, new.journal_sc
    )
    SELECT cte.oci, cte.citing, cte.cited, cte.citing_pub_year, cte.citing_pub_month, cte.citing_pub_date,
           cte.time_span, cte.author_sc, cte.journal_sc
    FROM cte
    JOIN open_citations oc
      ON oc.oci = cte.oci AND (oc.citing, oc.cited, oc.citing_pub_year, oc.citing_pub_month, oc.citing_pub_date,
                               oc.time_span,
                               oc.author_sc, oc.journal_sc) IS DISTINCT FROM (cte.citing, cte.cited,
                                                                              cte.citing_pub_year, cte.citing_pub_month,
                                                                              cte.citing_pub_date, cte.time_span,
                                                                              cte.author_sc, cte.journal_sc)
    ON CONFLICT(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date, time_span, author_sc, --
      journal_sc)
      -- NOP, but DO UPDATE is needed to set FOUND
      DO UPDATE SET oci = excluded.oci;
    IF found THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citations_looping(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                       time_span, author_sc, journal_sc)
    SELECT new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
           to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc
    FROM open_citations oc
    WHERE oc.citing = lower(new.cited)
      AND oc.cited = lower(new.citing)
    ON CONFLICT(oci)
      -- NOP, but DO UPDATE is needed to set FOUND
      DO UPDATE SET oci = excluded.oci;
    IF found THEN
      RETURN NULL;
    END IF;

    INSERT INTO open_citations_parallel(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                                        time_span, author_sc, journal_sc)
    SELECT new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
           to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc
    FROM open_citations oc
    WHERE oc.citing = lower(new.citing)
      AND oc.cited = lower(new.cited)
    ON CONFLICT(oci)
      -- NOP, but DO UPDATE is needed to set FOUND
      DO UPDATE SET oci = excluded.oci;
    IF found THEN
      RETURN NULL;
    END IF;

    /*
    TBD This runs into deadlocks e.g. with 8 parallel load jobs x 10,000 record batches, for example:
      ```
      ERROR:  deadlock detected
      DETAIL:  Process 3814937 waits for ShareLock on transaction 23722; blocked by process 3814933.
      Process 3814933 waits for ShareLock on transaction 23723; blocked by process 3814937.
      HINT:  See server log for query details.
      CONTEXT:  while inserting index tuple (4761626,35) in relation "open_citations"
      SQL statement [skipped] ...
      COPY stg_open_citations, line 9537:
      "02003030809361525283429370200020037050403090603-020010001063619371110231312370200000737000537000007,..."
      ```
      The ETL completes successfully with 4 parallel load jobs x 10,000 record batches.
    */
    INSERT INTO open_citations(oci, citing, cited, citing_pub_year, citing_pub_month, citing_pub_date,
                               time_span, author_sc, journal_sc)
    VALUES (new.oci, new.citing, new.cited, extract_year(new.creation), extract_month(new.creation),
            to_date(new.creation), to_interval(new.timespan), new.author_sc, new.journal_sc)
    ON CONFLICT(oci) DO NOTHING;

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

DROP TRIGGER IF EXISTS stg_open_citations_trg ON stg_open_citations;
CREATE TRIGGER stg_open_citations_trg
  INSTEAD OF INSERT
  ON stg_open_citations
  FOR EACH ROW
EXECUTE FUNCTION trg_transform_and_load_open_citation();