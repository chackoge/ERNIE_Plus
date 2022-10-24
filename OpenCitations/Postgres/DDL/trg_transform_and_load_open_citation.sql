-- trg_transform_and_load_open_citation(): routine
CREATE OR REPLACE FUNCTION trg_transform_and_load_open_citation() --
  RETURNS TRIGGER
  LANGUAGE plpgsql --
AS $block$
BEGIN
  IF (tg_op = 'INSERT') THEN
    INSERT INTO open_citations(oci, citing, cited, creation_date, time_span)
    VALUES
      (new.oci,
       new.citing,
       new.cited,
       make_date(cast(left(new.creation, 4) AS INT), cast(coalesce(nullif(substr(new.creation, 6, 2), ''), '6') AS INT),
                 cast(coalesce(nullif(substr(new.creation, 9), ''), '15') AS INT)),
       CASE
         WHEN left(new.timespan, 1) = '-'
           THEN -CAST(SUBSTR(new.timespan, 2) AS INTERVAL)
         ELSE CAST(new.timespan AS INTERVAL)
       END)
        ON CONFLICT (oci) DO UPDATE SET citing = excluded.citing,
          cited = excluded.cited,
          time_span = excluded.time_span,
          creation_date = excluded.creation_date;

    RETURN new;
  END IF;
  RAISE 'Operation % is not supported', tg_op;
END; $block$;