#!/usr/bin/env bash

usage() {
  cat <<'HEREDOC'
NAME

    neo4j_bulk_import.sh -- loads CSVs in bulk to Neo4j 4+

SYNOPSIS

    neo4j_bulk_import.sh DB_name node_label edge_label [nodes_file] [edges_file]
    neo4j_bulk_import.sh -h: display this help

DESCRIPTION

    Bulk imports to a new DB (it must not exist) and switches to this DB.
    Data for failed imports will be automatically removed.

    WARNING: Neo4j service is restarted on success.

    The following options are available:

    DB_name       Neo4j DB name. Use simple ascii characters, numbers, dots and dashes only.

    nodes_file    defaults to `nodes.csv`. The headers should conform to Neo4j import requirements:
      * `:ID`-tagged column is required. It is expected to contain numerical unique ids.

    edges_file    defaults to `edges.csv`. The headers should conform to Neo4j import requirements:
      * `:START_ID` and `:END_ID` columns are required.
        * They expected to contain only existing node ids from the nodes file.

ENVIRONMENT

    * Executing user must be able to run `systemctl`: either run the script under `root` or enable this via PolKit.

    * Executing user must be a member of the `neo4j` group

    * Neo4j must be set up to allow bulk import for the `neo4j` group:
      * `sudo chmod -R g+w /etc/neo4j /var/log/neo4j {dbms.directories.data}`

EXAMPLES

    To find all occurrences of the word `patricia' in a file:

        $ neo4j_bulk_import.sh Pub Cites

v2.0                                     August 2021                                   Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 1
}

set -e
set -o pipefail

[[ $1 == "-h" || $# -lt 3 ]] && usage

# Get a script directory, same as by $(dirname $0)
readonly SCRIPT_DIR=${0%/*}
readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)

readonly DB_NAME="$1"
readonly NODE_LABEL="$2"
readonly EDGE_LABEL="$3"
readonly NODES_FILE="${4:-nodes.csv}"
readonly EDGES_FILE="${5:-edges.csv}"

# `${USER:-${USERNAME:-${LOGNAME}}}` might be not available inside Docker containers
echo -e "\n# neo4j-switch-db.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

if ! command -v cypher-shell >/dev/null; then
  echo "Please install Neo4j"
  exit 1
fi

if ! command -v pcregrep >/dev/null; then
  echo "Please install pcre"
  exit 1
fi

readonly DB_DIR=$(pcregrep -o1 '^dbms\.directories\.data=(.*)' /etc/neo4j/neo4j.conf)

echo "Loading data into ${DB_NAME}"
if ! neo4j-admin import --report-file=/dev/null "--nodes=${NODE_LABEL}=${NODES_FILE}" --id-type=INTEGER \
  "--relationships=${EDGE_LABEL}=${EDGES_FILE}" "--database=${DB_NAME}"; then
   rm -rf "${DB_DIR}/databases/${DB_NAME}" "${DB_DIR}/transactions/${DB_NAME}"
   exit 1
fi
chgrp -R neo4j "${DB_DIR}/databases/${DB_NAME}" "${DB_DIR}/transactions/${DB_NAME}"
chmod -R g+w "${DB_DIR}/databases/${DB_NAME}" "${DB_DIR}/transactions/${DB_NAME}"

# The new DB don't become available until the service is restarted
"${ABSOLUTE_SCRIPT_DIR}/neo4j-switch-db.sh" "${DB_NAME}"

exit 0
