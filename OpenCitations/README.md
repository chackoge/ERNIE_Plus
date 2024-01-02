# ETL for OpenCitations #

OpenCitations ETL loads Open Citations data into a Postgres DB.

## OpenCitations Index ##

1. Download the latest Index CSVs from [OpenCitations](https://opencitations.net/download#index).
2. Unzip all ZIPs into a single CSV directory.
3. Create [Postgres data structures](OpenCitations/Postgres/DDL/open_citations_ddl.sql).
4. Run ETL, e.g. for 4 parallel jobs and batches of 10,000 records:
```Bash
./load-open-citations-index.sh -j 4 -s 10000 -d /data1/open_citations/csv -c
```
  * Scaling up the number of parallel jobs may lead to deadlock errors

ETL creates normalized data in the following tables:
* `open_citations`: Crossref open DOI-to-DOI citations excluding citation anomalies

Anomalies:
* `open_citations_duplicate`: citations with a duplicate OCI to `open_citations` but different data in an other column
* `open_citations_parallel`: citations that parallel (citing -> cited) in `open_citations`
* `open_citations_self`: citations with citing = cited
* `open_citations_looping`: citations that loop back (cited -> citing) comparing with `open_citations`
* `open_citations_no_valid_dating`: citations where the citing publication has either unknown (blank) date or the 
future year