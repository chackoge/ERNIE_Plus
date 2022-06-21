#!/usr/bin/env bash
EXEC_PREFIX=/usr/pgsql-12
$EXEC_PREFIX/bin/pg_dump --file=open_citations.dump --format=custom --table=open_citations
