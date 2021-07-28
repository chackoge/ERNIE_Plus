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

    DB_name       Neo4j DB name (spaces will be replaced by underscores)
    nodes_file    defaults to `nodes.csv`. The headers should conform to Neo4j import requirements:
      * :ID tagged column is required. It is expected to be of integer type.

    edges_file    defaults to `edges.csv`. The headers should conform to Neo4j import requirements:
      * :START_ID and :END_ID tagged columns are required

ENVIRONMENT

    Executing user must be a sudoer.

EXAMPLES

    To find all occurrences of the word `patricia' in a file:

        $ neo4j_bulk_import.sh Pub Cites

HEREDOC
  exit 1
}

set -e
set -o pipefail

[[ $1 == "-h" || $# -lt 3 ]] && usage

# Get a script directory, same as by $(dirname $0)
readonly SCRIPT_DIR=${0%/*}
readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)

#readonly WORK_DIR=${1:-${ABSOLUTE_SCRIPT_DIR}/build} # $1 with the default
#if [[ ! -d "${WORK_DIR}" ]]; then
#  mkdir "${WORK_DIR}"
#  chmod g+w "${WORK_DIR}"
#fi
#cd "${WORK_DIR}"
#echo -e "\n## Running under ${USER}@${HOSTNAME} in ${PWD} ##\n"

readonly DB_NAME="${1// /_}"
readonly NODE_LABEL="$2"
readonly EDGE_LABEL="$3"
readonly NODES_FILE="${4:-nodes.csv}"
readonly EDGES_FILE="${5:-edges.csv}"
#readonly USER_PASSWORD="$5"
#if [[ $5 ]]; then
#  readonly DB_PREFIX="${5// /_}-"
#fi

echo -e "\n## Running under ${USER}@${HOSTNAME} at ${PWD} ##\n"

if ! command -v cypher-shell >/dev/null; then
  echo "Please install Neo4j"
  exit 1
fi

if ! command -v pcregrep >/dev/null; then
  echo "Please install pcre"
  exit 1
fi

# region Generate a unique DB_NAME
#file_date1=$(date -r "${NODES_FILE}" +%F-%H-%M-%S)
#file_date2=$()
#if [[ ${file_date1} > ${file_date2} ]]; then
#  db_ver="${file_date1}"
#else
#  db_ver="${file_date2}"
#fi
#readonly DB_NAME="${DB_PREFIX}v${db_ver}"
# endregion

readonly DB_DIR=$(pcregrep -o1 '^dbms\.directories\.data=(.*)' /etc/neo4j/neo4j.conf)

sudo -u neo4j bash -c "set -e
  echo 'Loading data into ${DB_NAME}'
  if ! neo4j-admin import --report-file=/dev/null --verbose '--nodes=${NODE_LABEL}=${NODES_FILE}' --id-type=INTEGER \\
    '--relationships=${EDGE_LABEL}=${EDGES_FILE}' '--database=${DB_NAME}'; then
     rm -rf '${DB_DIR}/databases/${DB_NAME}'
     exit 1
  fi"

#echo "Loading data into ${DB_NAME}"
#neo4j-admin import "--nodes=${NODE_LABEL}=${NODES_FILE}" --id-type=INTEGER \
#  "--relationships=${EDGE_LABEL}=${EDGES_FILE}" "--database=${DB_NAME}"

# The new DB don't become available until the service is restarted
"${ABSOLUTE_SCRIPT_DIR}/neo4j-switch-db.sh" "${DB_NAME}"

exit 0
