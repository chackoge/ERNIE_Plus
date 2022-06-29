  WITH in_degrees AS (
    SELECT oc.cited AS node_id, COUNT(oc.citing) AS in_degree
      FROM open_citations oc
--      WHERE oc.cited = '10.1111/j.1467-954x.2011.02033.x'
     GROUP BY oc.cited
  ),
    out_degrees AS (
      SELECT oc.citing AS node_id, COUNT(oc.cited) AS out_degree
        FROM open_citations oc
--        WHERE oc.citing = '10.1111/j.1467-954x.2011.02033.x'
       GROUP BY oc.citing
    )
SELECT
  coalesce(id.node_id, od.node_id) AS node_id, id.in_degree, od.out_degree, id.in_degree + od.out_degree AS total_degree
  FROM in_degrees id
  FULL JOIN out_degrees od
            ON od.node_id = id.node_id;

  SELECT oc.citing, oc.cited
    FROM open_citations oc
   WHERE oc.citing = '10.1111/j.1467-954x.2011.02033.x' OR oc.cited = '10.1111/j.1467-954x.2011.02033.x'
   GROUP BY;

  SELECT oc.citing, oc.cited
    FROM open_citations oc
    JOIN cr_publications citing_cp
         ON citing_cp.doi = oc.citing
    JOIN cr_publications cited_cp
         ON cited_cp.doi = oc.cited;