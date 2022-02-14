CREATE OR REPLACE VIEW dimensions.citing_pubs AS
SELECT e12sd.citing_integer_id AS focal_int_id, e12sn.integer_id, e12sn.in_degree
  FROM dimensions.exosome_1900_2010_sabpq_nodelist e12sn
  JOIN dimensions.exosome_1900_2010_sabpq_deduplicated e12sd
       ON e12sd.cited_integer_id = e12sn.integer_id;

CREATE OR REPLACE VIEW dimensions.citing_counts AS
SELECT e12sd.citing_integer_id, COUNT(1) AS r_citing
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated e12sd
  JOIN dimensions.citing_pubs cp
       ON e12sd.citing_integer_id = cp.focal_int_id AND e12sd.cited_integer_id IN (
         SELECT citing_integer_id
           FROM dimensions.exosome_1900_2010_sabpq_deduplicated
          WHERE cited_integer_id = cp.integer_id --AND citing_integer_id <> citing_int_id
       )
 GROUP BY e12sd.citing_integer_id;

CREATE OR REPLACE VIEW dimensions.cited_counts AS
SELECT e12sd.citing_integer_id, COUNT(1) AS r_cited
  FROM dimensions.exosome_1900_2010_sabpq_deduplicated e12sd
  JOIN dimensions.citing_pubs cp
       ON e12sd.citing_integer_id = cp.focal_int_id AND e12sd.cited_integer_id IN (
         SELECT cited_integer_id
           FROM dimensions.exosome_1900_2010_sabpq_deduplicated
          WHERE citing_integer_id = cp.integer_id --AND citing_integer_id <> citing_int_id
       )
 GROUP BY e12sd.citing_integer_id;

SELECT SUM(count) AS tr_citing_count
FROM dimensions.citing_pubs cp;