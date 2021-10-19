#!/usr/bin/env bash

usage() {
  cat << 'HEREDOC'
data_file_name

    load-clusters.sh -- load cluster data into Postgres

SYNOPSIS

    load-clusters.sh cluster_type [-v clustering_version_opt] data_file [...]
    load-clusters.sh -h: display this help

DESCRIPTION

    Load cluster data into Postgres.

    The following options are available:

    cluster_type        one of:
                          * ikc: (node_seq_id, cluster_no, min_k, cluster_modularity), CSV
                          * clustering: (cluster_no, node_id), space-separated

    clustering_version_opt  optional, defaults to data_file name without extension

EXAMPLES

    To find all occurrences of the word `patricia' in a file:

        $ load-clusters.sh ikc ../ikc/testing_k5_b0.csv

v1.0                                   October 2021                                   Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 1
}

set -e
set -o pipefail

if [[ $1 == "-h" ]]; then
  usage
fi
readonly CLUSTER_TYPE=$1
shift

# Get a script directory, same as by $(dirname $0)
readonly SCRIPT_DIR=${0%/*}
#readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)

#readonly WORK_DIR=${1:-${ABSOLUTE_SCRIPT_DIR}/build} # $1 with the default
#if [[ ! -d "${WORK_DIR}" ]]; then
#  mkdir "${WORK_DIR}"
#  chmod g+w "${WORK_DIR}"
#fi
#cd "${WORK_DIR}"

# `${USER:-${USERNAME:-${LOGNAME}}}` might be not available inside Docker containers
echo -e "\n# load-clusters.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

while (($# > 0)); do
  if [[ $1 == "-v" ]]; then
    shift
    clustering_version_opt=$1
    shift
  else
    unset clustering_version_opt
  fi

  data_file=$1

  # Remove the longest `*/` prefix
  data_file_name_with_ext=${data_file##*/}

  if [[ "${data_file_name_with_ext}" != *.* ]]; then
    data_file_name_with_ext=${data_file_name_with_ext}.
  fi

  # Remove the last (shortest) `.*` suffix
  data_file_name=${data_file_name_with_ext%.*}
  clustering_version=${clustering_version_opt:-$data_file_name}

  echo "Loading clustering version $clustering_version from $data_file"
  psql -f "${SCRIPT_DIR}/stage-clusters-$CLUSTER_TYPE.sql" -v schema=clusters -v "data_file=$data_file"
  psql -f "${SCRIPT_DIR}/load-clusters.sql" -v schema=clusters -v "clustering_version=${clustering_version}"
  echo -e "Loaded.\n"

  shift
done
