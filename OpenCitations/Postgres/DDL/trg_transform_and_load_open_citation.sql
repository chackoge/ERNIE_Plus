CREATE OR REPLACE FUNCTION trg_transform_and_load_open_citation() RETURNS TRIGGER AS $block$
  --@formatter:off To match with stored line numbers avoid wrapping or formatting above.
BEGIN --
  IF (TG_OP = 'INSERT') THEN
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
       END);

    RETURN NEW;
  END IF;
  RAISE 'Operation % is not supported', TG_OP;
--@formatter:on
END; $block$ LANGUAGE plpgsql;