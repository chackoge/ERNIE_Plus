# ETL for OpenCitations #

OpenCitations ETL loads Open Citations data into a Postgres DB.

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