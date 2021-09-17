#!/usr/bin/env bash

usage() {
  cat << 'HEREDOC'
NAME

    neo4j_bulk_import.sh -- loads CSVs in bulk to Neo4j 4+

SYNOPSIS

    neo4j_bulk_import.sh [-s] DB_name nodes_file1 [nodes_file2] [...]
    neo4j_bulk_import.sh -h: display this help

DESCRIPTION

    Bulk imports to a new DB (it must not exist) and, optionally, switches to this DB.
    Data for failed imports will be automatically removed.

    The following options are available:

    -s            Switch to a new DB and restart the Neo4j service on success.
                  Executing user must be able to run `systemctl`: either run the script under `root` or enable this
                  via PolKit.

    DB_name       Neo4j DB name. Use simple ascii characters, numbers, dots and dashes only.

    nodes_file    The filename would be used as a node label for all the nodes in this file.
                  The nodes file CSV headers should conform to Neo4j import requirements + using numeric ids:
                  * `:ID`-tagged column is required. It is expected to contain unique numeric node ids.

                  Corresponding edges are loaded from `{nodes_file}-*.csv` and the edges filename would be used
                  as an edge label.
                  The edges file CSV headers should conform to Neo4j import requirements:
                  * `:START_ID` and `:END_ID` columns are required.
                    * They expected to contain only existing node ids from the nodes file.

ENVIRONMENT

    * Executing user must be `neo4j`, `root` or a member of the `neo4j` group, in which case Neo4j must be set up to
    allow bulk import for the `neo4j` group:
      * `sudo chmod -R g+w /etc/neo4j /var/log/neo4j {dbms.directories.data}`

EXAMPLES

    To load publications and clusters from `pub.csv`/`pub-cites.csv` + `cluster.csv`/`cluster-contains.csv`:

        $ neo4j_bulk_import.sh ernieplus-2021-09-15 pub cluster

v3.0                                   September 2021                                  Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 1
}

set -e
set -o pipefail

# If a character is followed by a colon, the option is expected to have an argument
while getopts sh OPT; do
  case "$OPT" in
    s)
      readonly SWITCH_OPT=-r
      ;;
    *) # -h or `?`: an unknown option
      usage
      ;;
  esac
done
shift $((OPTIND - 1))

# Process positional parameters
readonly DB_NAME="$1"
shift
[[ $1 == "" ]] && usage
while (($# > 0)); do
  nodes_file="$1"
  echo "Loading nodes from $nodes_file"

  # Remove longest */ prefix
  name_with_ext=${nodes_file##*/}

  if [[ "${name_with_ext}" != *.* ]]; then
    name_with_ext=${name_with_ext}.
  fi
  # Remove longest *. prefix
#   ext=${name_with_ext##*.}

  # Remove shortest .* suffix
  name=${name_with_ext%.*}

  if [[ "${nodes_file}" != */* ]]; then
    nodes_file=./${nodes_file}
  fi
  # Remove shortest /* suffix
  dir=${nodes_file%/*}

  file_opts="$file_opts --nodes=${name}=$1"
  for edges_file in "$dir/$name"-*.csv; do
    echo "Loading edges from $edges_file"
    # Remove longest */ prefix
    name_with_ext=${edges_file##*/}

    if [[ "${name_with_ext}" != *.* ]]; then
      name_with_ext=${name_with_ext}.
    fi
    # Remove longest *. prefix
#    ext=${name_with_ext##*.}

    # Remove shortest .* suffix
    name=${name_with_ext%.*}

    file_opts="$file_opts --relationships=${name}=${edges_file}"
  done

  shift
done

# Get a script directory, same as by $(dirname $0)
readonly SCRIPT_DIR=${0%/*}
readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)

# `${USER:-${USERNAME:-${LOGNAME}}}` might be not available inside Docker containers
echo -e "\n# neo4j-switch-db.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

if ! command -v cypher-shell > /dev/null; then
  echo "Please install Neo4j"
  exit 1
fi

if ! command -v pcregrep > /dev/null; then
  echo "Please install pcre"
  exit 1
fi

readonly DB_DIR=$(pcregrep -o1 '^dbms\.directories\.data=(.*)' /etc/neo4j/neo4j.conf)

echo "Loading into the ${DB_NAME} DB"

# shellcheck disable=SC2086 # expanding $file_opts to multiple words by design
if ! neo4j-admin import "--database=${DB_NAME}" $file_opts --id-type=INTEGER --report-file=/dev/null; then
  rm -rf "${DB_DIR}/databases/${DB_NAME}" "${DB_DIR}/transactions/${DB_NAME}"
  exit 1
fi
chgrp -R neo4j "${DB_DIR}/databases/${DB_NAME}" "${DB_DIR}/transactions/${DB_NAME}"
chmod -R g+w "${DB_DIR}/databases/${DB_NAME}" "${DB_DIR}/transactions/${DB_NAME}"

"${ABSOLUTE_SCRIPT_DIR}/neo4j-switch-db.sh" $SWITCH_OPT "${DB_NAME}"

exit 0
