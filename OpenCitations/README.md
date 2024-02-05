# ETL for OpenCitations #

OpenCitations ETL loads Open Citations data into a Postgres DB.

Requirements:

Postgres 15+ with the default Postgres DB which has the following:
* `open_citations_tbs` tablespace with 300 GB available disk space
* `index_tbs` tablespace with 250 GB available disk space
* A user with the name = {OS executing user} and the following Postgres privileges or a superuser role:
  * `pg_read_server_files`
  * INSERT on `public.*open_citations*` tables and views
  * EXECUTE on `public.to_date()` and `public.to_interval()` functions
  * CREATE on SCHEMA `public`

## OpenCitations Meta ##

1. Download the latest Meta ZIP from [OpenCitations](https://opencitations.net/download#index).
2. Unzip.
3. Create [Postgres data structures](Postgres/DDL/open_citations_ddl.sql).
4. Run ETL, for example, using 64 parallel jobs:
```Bash
./load-open-citations-meta.sh -j 64 -d /data1/open_citations/open_citations_meta-v6-2023-11-30/csv -c
```
* `-c` is a recommended option to clean, that is, remove completed CSVs
5. Download and unZIP the latest BR OMID map from [OpenCitations](https://opencitations.net/download#index).

ETL creates publications in the following table:
* `open_citations_pubs`: bibliographic resources

Estimated load time v6-2023-11-30: 11-12 minutes
* Server: 96 CPU cores (48 x 2) and 256 GB RAM
* Load with 64 parallel jobs

## OpenCitations Index ##

1. Download the latest Index CSVs from [OpenCitations](https://opencitations.net/download#index).
2. Unzip all ZIPs into a single CSV directory.
3. Create [Postgres data structures](Postgres/DDL/open_citations_ddl.sql).
4. Run ETL, for example, using four parallel jobs and batches of 10,000 records:
```Bash
./load-open-citations-index.sh -j 4 -s 10000 -d /data1/open_citations/csv -c
```
  * `-c` is a recommended option to clean, that is, remove completed CSVs
  * Scaling up the number of parallel jobs may lead to deadlock errors

ETL creates citations in the following tables:
* `open_citations`: Crossref open DOI-to-DOI citations excluding citation anomalies

Anomalies:
* `open_citations_duplicate` are citations with a duplicate OCI to another one in `open_citations` but different data in 
another column.
  Full duplicates are ignored.
* `open_citations_parallel` are citations that parallel citing -> cited in `open_citations`
* `open_citations_self` are citations with citing = cited
* `open_citations_looping` are citations that loop back comparing to another one in `open_citations`: cited -> citing
* `open_citations_no_valid_dating` are citations from the citing publication with either unknown / blank date or a
future year

Estimated load time v2023-11-29: 24-25 hours
* Server: 96 CPU cores (48 x 2) and 256 GB RAM
* Load with four parallel jobs, 10,000 record batches