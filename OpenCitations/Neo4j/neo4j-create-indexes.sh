#!/usr/bin/env bash

usage() {
  cat <<'HEREDOC'
NAME

    neo4j-create-indexes.sh -- do something

SYNOPSIS

    neo4j-create-indexes.sh node_label indexed_property_list ...
    neo4j-create-indexes.sh -h: display this help

DESCRIPTION

    Creates requested indexes and waits until they become available.

    The following options are available:

    node_label             For example: Pub
    indexed_property_list  A single property or a comma-seprated list of properties for a composite index

EXAMPLES

    To find all occurrences of the word `patricia' in a file:

        $ neo4j-create-indexes.sh Pub doi issn,year

AUTHOR(S)

    Created by Dmitriy "DK" Korobskiy, May 2021
HEREDOC
  exit 1
}

set -e
set -o pipefail

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
[[ $1 == "" ]] && usage
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
[[ $1 == "" ]] && usage
readonly NODE_LABEL=$1
shift
declare -a indexed_property_list
while (($# > 0)); do
  indexed_property_list+=("$1")
  shift
done

# Get a script directory, same as by $(dirname $0)
#readonly SCRIPT_DIR=${0%/*}
#readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)
#
#readonly WORK_DIR=${1:-${ABSOLUTE_SCRIPT_DIR}/build} # $1 with the default
#if [[ ! -d "${WORK_DIR}" ]]; then
#  mkdir "${WORK_DIR}"
#  chmod g+w "${WORK_DIR}"
#fi
#cd "${WORK_DIR}"
echo -e "\n## Running under ${USER}@${HOSTNAME} in ${PWD} ##\n"

for item in "${indexed_property_list[@]}"; do
  # Qualify all properties in the list with `n.`
  index_spec="n.${item//,/, n.}"
  echo "Creating index for (n:${NODE_LABEL}) on ${index_spec}"
  cypher-shell <<HEREDOC
CREATE INDEX IF NOT EXISTS FOR (n:${NODE_LABEL}) ON (${index_spec});
HEREDOC
done

echo "Wait until index creation finishes..."
cypher-shell <<HEREDOC
// Use timeOutSeconds = 600 (default = 300)
CALL db.awaitIndexes(600);
HEREDOC

exit 0