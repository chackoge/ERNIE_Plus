WITH
  s_b_table AS ( -- getting the dois for publications that were cited by <SEED>'s ids
    -- <SEED> (citing) -> publications (cited)
  SELECT
    <SEED>.doi AS citing,
    publications.doi AS cited,
    citations.id AS citing_id,
    publications.id AS cited_id,
    publications.year AS cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications
  CROSS JOIN
    UNNEST(publications.citations) citations,
    `<SEED PUBLICATIONS>` <SEED>
  WHERE
    <SEED>.id = citations.id ),
  s_b_translate AS ( -- adding citing year information but not author list to s_b_table
  SELECT
    s_b_table.citing,
    s_b_table.cited,
    s_b_table.citing_id,
    s_b_table.cited_id,
    publications.year AS citing_year,
    s_b_table.cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications,
    s_b_table
  WHERE
    s_b_table.citing_id = publications.id ),
  a_s_table AS ( -- getting the dimensions id for publications that cite <SEED>'s ids
  SELECT
    citations.id AS citing_id,
    <SEED>.doi AS cited,
    <SEED>.id AS cited_id,
    publications.year AS cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications
  CROSS JOIN
    UNNEST(publications.citations) citations,
    `<SEED PUBLICATIONS>` <SEED>
  WHERE
    <SEED>.id = publications.id ),
  a_s_translate AS ( -- translating the a_s_table's dimensions id into dois
  SELECT
    publications.doi AS citing,
    a_s_table.cited AS cited,
    publications.id AS citing_id,
    a_s_table.cited_id,
    publications.year AS citing_year,
    a_s_table.cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications,
    a_s_table
  WHERE
    a_s_table.citing_id = publications.id ),
  asb_table AS (
  SELECT
    DISTINCT citing_id AS id
  FROM
    a_s_translate
  UNION DISTINCT
  SELECT
    DISTINCT cited_id AS id
  FROM
    a_s_translate
  UNION DISTINCT
  SELECT
    DISTINCT citing_id AS id
  FROM
    s_b_translate
  UNION DISTINCT
  SELECT
    DISTINCT cited_id AS id
  FROM
    s_b_translate ),
  p_asb_table AS ( -- getting the dimensions id for publications that cite the ids of asb_table (A,S, or B)
    -- publications.citations (citing) -> asb_table (cited)
  SELECT
    citations.id AS citing_id,
    publications.doi AS cited,
    asb_table.id AS cited_id,
    publications.year AS cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications
  CROSS JOIN
    UNNEST(publications.citations) citations,
    asb_table
  WHERE
    asb_table.id = publications.id ),
  p_asb_translate AS ( -- translating the p_asb_table's dimensions id into dois
  SELECT
    publications.doi AS citing,
    p_asb_table.cited AS cited,
    publications.id AS citing_id,
    p_asb_table.cited_id,
    publications.year AS citing_year,
    p_asb_table.cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications,
    p_asb_table
  WHERE
    p_asb_table.citing_id = publications.id ),
  asb_q_table AS ( -- getting the dois for publications that were cited by the ids of asb_table (A,S, or B)
    -- asb_table (citing) -> publications (cited)
  SELECT
    publications.doi AS cited,
    citations.id AS citing_id,
    publications.id AS cited_id,
    publications.year AS cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications
  CROSS JOIN
    UNNEST(publications.citations) citations,
    asb_table
  WHERE
    asb_table.id = citations.id ),
  asb_q_translate AS ( -- adding citing year information but not author list to asb_q_table
  SELECT
    publications.doi AS citing,
    asb_q_table.cited,
    asb_q_table.citing_id,
    asb_q_table.cited_id,
    publications.year AS citing_year,
    asb_q_table.cited_year,
  FROM
    `dimensions-ai.data_analytics.publications` publications,
    asb_q_table
  WHERE
    asb_q_table.citing_id = publications.id ),
  cited_citing AS(
  SELECT
    citing,
    cited,
    citing_id,
    cited_id,
    citing_year,
    cited_year,
    's_b' AS network_type,
  FROM
    s_b_translate
  UNION ALL
  SELECT
    citing,
    cited,
    citing_id,
    cited_id,
    citing_year,
    cited_year,
    'a_s' AS network_type,
  FROM
    a_s_translate
  UNION ALL
  SELECT
    citing,
    cited,
    citing_id,
    cited_id,
    citing_year,
    cited_year,
    'p_asb' AS network_type,
  FROM
    p_asb_translate
  UNION ALL
  SELECT
    citing,
    cited,
    citing_id,
    cited_id,
    citing_year,
    cited_year,
    'asb_q' AS network_type,
  FROM
    asb_q_translate )
SELECT
  citing,
  cited,
  citing_id,
  cited_id,
  citing_year,
  cited_year,
  network_type
FROM
  cited_citing;
