#!/usr/bin/env bash

usage() {
  cat << 'HEREDOC'
data_file_name

    load-clusters.sh -- load cluster data into Postgres

SYNOPSIS

    load-clusters.sh [-f clustering_format] data_file [...]
    load-clusters.sh -h: display this help

DESCRIPTION

    Load cluster data of one of supported formats into Postgres.

    The following options are available:

      -f clustering_format

        CSV data format for all files: optional, based on file extension by default, per `data_file`.
        * `core_analysis` (for `.clustering`): node_seq_id, cluster_no, core_classifier, cluster_modularity, mcd, cced
        * `ikc` (for `.csv`): node_seq_id, cluster_no, min_k, cluster_modularity

EXAMPLES

    To load data from the `ikc` format:

        $ load-clusters.sh ../ikc/testing_k5_b0.csv

v1.3                                   November 2021                                   Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 1
}

set -e
set -o pipefail

# If a character is followed by a colon, the option is expected to have an argument
while getopts f:h OPT; do
  case "$OPT" in
    f)
      readonly DEFAULT_FORMAT="$OPTARG"
      ;;
    *) # -h or `?`: an unknown option
      usage
      ;;
  esac
done
shift $((OPTIND - 1))

# Get a script directory, same as by $(dirname $0)
readonly SCRIPT_DIR=${0%/*}
#readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)

#readonly WORK_DIR=${1:-${ABSOLUTE_SCRIPT_DIR}/build} # $1 with the default
#if [[ ! -d "${WORK_DIR}" ]]; then
#  mkdir "${WORK_DIR}"
#  chmod g+w "${WORK_DIR}"
#fi
#cd "${WORK_DIR}"

trap "echo -e 'Done.\a'" EXIT

# `${USER:-${USERNAME:-${LOGNAME}}}` might be not available inside Docker containers
echo -e "\n# load-clusters.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

while (($# > 0)); do
  data_file=$1
  shift

  # Remove the longest `*/` prefix
  data_file_name_with_ext=${data_file##*/}
  if [[ "${data_file_name_with_ext}" != *.* ]]; then
    data_file_name_with_ext=${data_file_name_with_ext}.
  fi

  # Remove the last (shortest) `.*` suffix
  data_file_name=${data_file_name_with_ext%.*}

  clustering_version=$data_file_name
  format=$DEFAULT_FORMAT
  if [[ ! $format ]]; then
    # Remove the longest `*.` prefix
    ext=${data_file_name_with_ext##*.}
    
    case $ext in
      csv)
        format='ikc'
      ;;
      clustering)
        format='core_analysis'
      ;;
      *)
        >&2 echo "ERROR. Couldn't determine data format for \`$data_file\`: using extension \`$ext\`"
        exit 2
      ;;
    esac
  fi

  echo "Loading clustering version $clustering_version from $data_file using data format $format"
  psql -f "${SCRIPT_DIR}/stage-clusters-${format}.sql" -v schema=clusters <"$data_file"
  psql -f "${SCRIPT_DIR}/load-clusters.sql" -v schema=clusters -v "clustering_version=${clustering_version}"
  echo -e "Loaded.\n"
done
