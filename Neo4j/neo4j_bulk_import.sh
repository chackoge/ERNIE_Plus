#!/usr/bin/env bash

usage() {
  cat <<'HEREDOC'
NAME

    neo4j_bulk_import.sh -- loads CSVs in bulk to Neo4j 4+

SYNOPSIS

    neo4j_bulk_import.sh node_label edge_label [nodes_file] [edges_file] [DB_name_prefix]
    neo4j_bulk_import.sh -h: display this help

DESCRIPTION

    Bulk imports to a new `{DB_name_prefix-}v{file_timestamp}` DB and switches to this DB.
    WARNING: Neo4j service is restarted.

    Spaces are replaced by underscores in the `DB_name_prefix`.

    The following options are available:

    nodes_file    defaults to `nodes.csv`
    edges_file    defaults to `edges.csv`

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

[[ $1 == "-h" || $# -lt 2 ]] && usage

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

readonly NODE_LABEL="$1"
readonly EDGE_LABEL="$2"
readonly NODES_FILE="${3:-nodes.csv}"
readonly EDGES_FILE="${4:-edges.csv}"
#readonly USER_PASSWORD="$5"
if [[ $5 ]]; then
  readonly DB_PREFIX="${5// /_}-"
fi

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
file_date1=$(date -r "${NODES_FILE}" +%F-%H-%M-%S)
file_date2=$()
if [[ ${file_date1} > ${file_date2} ]]; then
  db_ver="${file_date1}"
else
  db_ver="${file_date2}"
fi
readonly DB_NAME="${DB_PREFIX}v${db_ver}"
# endregion

readonly DB_DIR=$(pcregrep -o1 'dbms\.directories\.data=(.*)' /etc/neo4j/neo4j.conf)

sudo -u neo4j bash -c "set -xe
  echo 'Loading data into ${DB_NAME}'
  neo4j-admin import --report-file=/dev/null --verbose '--nodes=${NODE_LABEL}=${NODES_FILE}' --id-type=INTEGER \\
    '--relationships=${EDGE_LABEL}=${EDGES_FILE}' '--database=${DB_NAME}' || rm -rf ${DB_DIR}/databases/${DB_NAME}"

#echo "Loading data into ${DB_NAME}"
#neo4j-admin import "--nodes=${NODE_LABEL}=${NODES_FILE}" --id-type=INTEGER \
#  "--relationships=${EDGE_LABEL}=${EDGES_FILE}" "--database=${DB_NAME}"

"${ABSOLUTE_SCRIPT_DIR}/neo4j_switch_db.sh" "${DB_NAME}" "$USER_PASSWORD"

exit 0
