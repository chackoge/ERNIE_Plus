#!/usr/bin/env bash

usage() {
  cat <<'HEREDOC'
NAME

    neo4j-import.sh -- loads CSVs in bulk to Neo4j 4+

SYNOPSIS

    neo4j-import.sh node_label nodes_file edge_label edges_file current_user_password [DB_name_prefix]
    neo4j-import.sh -h: display this help

DESCRIPTION

    Import in bulk to a new `{DB_name_prefix-}v{file_timestamp}` DB. ().

    The following options are available:

    nodes_file            Neo4j-compatible nodes CSV
    edges_file            Neo4j-compatible edges CSV
    current_user_password Linux User password
    DB_name_prefix        (Optional). Spaces will be replaced by `_` in the DB name.

ENVIRONMENT

    Executing user must be a sudoer.
    The current directory must be writeable for the `neo4j` user.

AUTHOR(S)

    Created by Dmitriy "DK" Korobskiy, May 2021
HEREDOC
  exit 1
}

set -e
set -o pipefail

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
# If a character is followed by a colon, the option is expected to have an argument

#while getopts vf:h OPT; do
#  case "$OPT" in
#    v)
#      readonly VERBOSE=true
#      ;;
#    f)
#      file="$OPTARG"
#      ;;
#    *) # -h or `?`: an unknown option
#      usage
#      ;;
#  esac
#done
#shift $((OPTIND - 1))

# Process positional parameters
readonly NODE_LABEL="$1"
readonly NODES_FILE="$2"
readonly EDGE_LABEL="$3"
readonly EDGES_FILE="$4"
readonly USER_PASSWORD="$5"
[[ $5 == "" ]] && usage
if [[ $6 ]]; then
  readonly DB_PREFIX="${6// /_}-"
fi

echo -e "\n## Running under ${USER}@${HOSTNAME} at ${PWD} ##\n"

if ! command -v neo4j-admin >/dev/null; then
  echo "Please install Neo4j"
  exit 1
fi

#region Generate a unique DB name
file_date1=$(date -r "${NODES_FILE}" +%F-%H-%M-%S)
file_date2=$(date -r "${EDGES_FILE}" +%F-%H-%M-%S)
if [[ ${file_date1} > ${file_date2} ]]; then
  db_ver="${file_date1}"
else
  db_ver="${file_date2}"
fi
db_name="${DB_PREFIX}v${db_ver}"
#endregion

# The current directory must be writeable for the neo4j user. Otherwise, it'd fail with the
# `java.io.FileNotFoundException: import.report (Permission denied)` error
echo "Loading data into ${db_name}"
# --bad-tolerance=<num>: # of bad relationships referring to missing nodes to tolerate
# Faile without using node and edge labels
if ! echo "$USER_PASSWORD" | sudo --stdin -u neo4j neo4j-admin import --nodes="${NODE_LABEL}=${NODES_FILE}" \
    --relationships="${EDGE_LABEL}=${EDGES_FILE}" --database="${db_name}" --bad-tolerance=0; then
  >&2 echo "Error! Removing ${db_name}"
  # TODO Replace hardcoded DB path
  echo "$USER_PASSWORD" | sudo --stdin -u neo4j rm -rf "/disk1/neo4j_data/databases/${db_name}"
  exit 1
fi

# The new database is not going to be available until it is started
"${ABSOLUTE_SCRIPT_DIR}/neo4j-switch-db.sh" "${db_name}" "$USER_PASSWORD"

exit 0
