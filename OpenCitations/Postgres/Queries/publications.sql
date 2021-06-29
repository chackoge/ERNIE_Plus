-- DOIs containing commas
SELECT doi, issn, published_year
  FROM cr_publications cp
 WHERE doi LIKE '%,%'
 LIMIT 1;

SELECT doi, issn, published_year
  FROM cr_publications cp
 WHERE doi LIKE '10.1001/jama.251.19.2504%';

SELECT doi, issn, published_year
  FROM cr_publications cp
 LIMIT 100;

SELECT *
  FROM cr_doi_pubids
 WHERE doi = '10.5575/geosoc.35.492';

SELECT cast(deposited_date_time AS DATE)
  FROM cr_doi_time_neither cdtn
 LIMIT 10;

SELECT doi, CAST(left(published_online, 4) AS SMALLINT) AS published_year
  FROM cr_doi_time_online cdto
 LIMIT 10;

SELECT oci, citing, cited, CAST(creation AS DATE), timespan, CAST(timespan AS INTERVAL)
  FROM oci_2019_1_63 o
 LIMIT 10;

SELECT oci, citing, cited, CAST(creation AS DATE), timespan
  FROM oci_2019_1_63 o
 WHERE timespan LIKE '-%'
 LIMIT 10;

SELECT oci, citing, cited, creation, timespan
  FROM oci_2019_1_63 o
 WHERE creation = '2019-02'rrs
LIMIT 10;

SELECT oci, creation, timespan
  FROM oci_2019_1_63 o
 WHERE length(creation) < 4
 LIMIT 10;

INSERT INTO cr_publications(doi, volume, pages, issn)
SELECT DISTINCT doi, volume, page, issn
  FROM cr_doi_pubids cdp;

INSERT INTO cr_publications(doi, deposited_date)
SELECT doi, cast(deposited_date_time AS DATE) AS deposited_date
  FROM cr_doi_time_neither cdtn
    ON CONFLICT (doi) DO UPDATE SET deposited_date = excluded.deposited_date;

INSERT INTO cr_publications(doi, published_year)
SELECT doi, CAST(left(published_online, 4) AS SMALLINT) AS published_year
  FROM cr_doi_time_online cdto
    ON CONFLICT (doi) DO UPDATE SET published_year = excluded.published_year;

INSERT INTO cr_publications(doi, published_year)
SELECT doi, CAST(left(published_print, 4) AS SMALLINT) AS published_year
  FROM cr_doi_time_print cdtp
    ON CONFLICT (doi) DO UPDATE SET published_year = excluded.published_year;

-- `least()` works fine here -- noinspection SqlSignature
INSERT INTO cr_publications(doi, published_year)
SELECT
  doi, least(CAST(left(published_print, 4) AS SMALLINT), CAST(left(published_online, 4) AS SMALLINT)) AS published_year
  FROM cr_doi_time_print_online cdtpo
    ON CONFLICT (doi) DO UPDATE SET published_year = excluded.published_year;

INSERT INTO cr_pub_authors(doi, given_name, family_name)
SELECT DISTINCT doi, given_name, family_name
  FROM cr_doi_author cda;

/*INSERT INTO open_citations(oci, citing, cited, creation_year, time_span)
SELECT
  oci,
  citing,
  cited,
  CAST(LEFT(creation, 4) AS SMALLINT),
  CASE WHEN left(timespan, 1) = '-' THEN -CAST(SUBSTR(timespan, 2) AS INTERVAL) ELSE CAST(timespan AS INTERVAL) END
FROM oci_2019_1_63 o;*/

-- noinspection SqlWithoutWhere
UPDATE open_citations oc
   SET creation_date = (
     SELECT
       make_date(cast(left(creation, 4) AS INT), cast(coalesce(nullif(substr(creation, 6, 2), ''), '6') AS INT),
                 cast(coalesce(nullif(substr(creation, 9), ''), '15') AS INT)) AS creation_date
       FROM oci_2019_1_63 o
      WHERE o.oci = oc.oci
   );