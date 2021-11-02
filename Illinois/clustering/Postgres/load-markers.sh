#!/usr/bin/env bash

usage() {
  cat << 'HEREDOC'
    load-markers.sh -- load cluster data into Postgres

SYNOPSIS

    load-markers.sh [-m MARKING_VERSION] data_file
    load-markers.sh -h: display this help

DESCRIPTION

    Load node markers into Postgres.

    The following options are available:

      -m MARKING_VERSION  optional, defaults to data file name

v1.3                                   November 2021                                   Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 1
}

set -e
set -o pipefail

# If a character is followed by a colon, the option is expected to have an argument
while getopts m:h OPT; do
  case "$OPT" in
    m)
      readonly MARKING_VERSION="$OPTARG"
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
echo -e "\n# load-markers.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

data_file=$1
shift

if [[ ! $MARKING_VERSION ]]; then
  # Remove the longest `*/` prefix
  data_file_name_with_ext=${data_file##*/}
  if [[ "${data_file_name_with_ext}" != *.* ]]; then
    data_file_name_with_ext=${data_file_name_with_ext}.
  fi

  # Remove the last (shortest) `.*` suffix
  data_file_name=${data_file_name_with_ext%.*}

  readonly MARKING_VERSION=$data_file_name
fi

echo "Loading marking version $MARKING_VERSION from $data_file"
# language=PostgresPLSQL
psql -f "${SCRIPT_DIR}/load-markers.sql" -v schema=clusters -v "marking_version=${MARKING_VERSION}" <"$data_file"
