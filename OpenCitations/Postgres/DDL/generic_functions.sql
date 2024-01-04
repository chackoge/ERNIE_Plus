\set ON_ERROR_STOP on
\set ECHO all

\if :{?schema}
SET search_path = :schema;
\endif

-- JetBrains IDEs: start execution from here
SET TIMEZONE = 'US/Eastern';

CREATE OR REPLACE FUNCTION extract_year(date_string TEXT) RETURNS SMALLINT
  /**
  Extracts year from YYYY[-MM][-DD] string
  */
RETURN cast(left(date_string, 4) AS SMALLINT);

CREATE OR REPLACE FUNCTION extract_month(date_string TEXT) RETURNS SMALLINT
  /**
  Extracts month from YYYY[-MM][-DD] string
  */
RETURN cast(nullif(substr(date_string, 6, 2), '') AS SMALLINT);

CREATE OR REPLACE FUNCTION to_date(date_string TEXT) RETURNS DATE
  /**
  Converts YYYY[-MM][-DD] string to a DATE
  @return NULL for incomplete dates
  */
RETURN CASE WHEN length(date_string) = length('YYYY-MM-DD') THEN to_date(date_string, 'YYYY-MM-DD') END;

CREATE OR REPLACE FUNCTION to_interval(signed_iso_8601_interval TEXT) RETURNS INTERVAL
  /**
  Converts [-]P{quantity}{unit}[{quantity}{unit} ...] string to an INTERVAL
  */
RETURN CASE
         WHEN left(signed_iso_8601_interval, 1) = '-' THEN -cast(substr(signed_iso_8601_interval, 2) AS INTERVAL)
         ELSE cast(signed_iso_8601_interval AS INTERVAL) END;
