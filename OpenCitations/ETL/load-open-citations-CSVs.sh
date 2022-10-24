#!/usr/bin/env bash

usage() {
  cat << 'HEREDOC'
NAME

    load-open-citations-CSVs.sh -- load Open Citations CSVs in parallel

SYNOPSIS

    load-open-citations-CSVs.sh [-r]
    load-open-citations-CSVs.sh -h: display this help

DESCRIPTION

    Load Open Citations CSVs in parallel from the current directory.

    The following options are available:

    -r    remove loaded CSVs (recommended to simplify error recovery)

ENVIRONMENT

    GNU `parallel` utility is required.

    The maximum number of parallel job slots = 64.

EXIT STATUS

    The load-open-citations-CSVs.sh utility exits with one of the following values:

    0     All files have been successfully loaded

    1-100 The number of failed load jobs. The process stops gracefully on the first error.

    255   Usage help is requested

v2.0                                    March 2022                                    Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 255
}

set -e
set -o pipefail

# If a colon follows a character, the option is expected to have an argument
while getopts rh OPT; do
  case "$OPT" in
    r)
      declare -rx REMOVE_LOADED=true
      ;;
    *) # -h or `?`: an unknown option
      usage
      ;;
  esac
done
shift $((OPTIND - 1))

if ! command -v parallel > /dev/null; then
  echo "Please install GNU parallel"
  exit 1
fi

# `${USER:-${USERNAME:-${LOGNAME}}}` might be not available inside Docker containers
echo -e "\n# load-open-citations-CSVs.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

# `\\copy` of large Open Citations CSVs (1.5-1.8 G) consumes a lot of memory, e.g. ≈ 100 G for 32 jobs.
# When the # of jobs is too large the entire machine might get overloaded.
readonly MAX_PARALLEL_JOBS=20

load_csv() {
  set -e
  set -o pipefail
  local file=$1
  echo "Processing ${file} ..."

  if [[ "${file}" != */* ]]; then
    file=./${file}
  fi
  # Remove shortest /* suffix
  dir=${file%/*}
  # dir = '.' for files in the current directory

  # Remove longest */ prefix
  name_with_ext=${file##*/}

  absolute_file_dir=$(cd "${dir}" && pwd)
  absolute_file_path="${absolute_file_dir}/${name_with_ext}"

  # Ignoring extra columns `journal_sc, author_sc` from `oci, citing, cited, creation, timespan, journal_sc, author_sc`
  # could be done via e.g., `COPY ... FROM PROGRAM 'cut -d "," -f 1-5 ':'file'''`, but it is probably not worth it
  # performance-wise.

  # language=PostgresPLSQL
  psql -v ON_ERROR_STOP=on << HEREDOC
    \\copy stg_open_citations(oci, citing, cited, creation, timespan, journal_sc, author_sc) from '${absolute_file_path}' (FORMAT CSV, HEADER ON)
HEREDOC

  echo "Loaded ${file}"
  if [[ $REMOVE_LOADED ]]; then
    rm -v "${file}"
  fi
}
export -f load_csv

echo "Starting data load: appending all records to existing Open Citations data."

# Piping to `parallel` is done by design here to handle a large number of files potentially
# shellcheck disable=SC2016 # `--tagstring` tokens are expanded by GNU `parallel`
find . -maxdepth 1 -type f -name '*.csv' -print0 | parallel -0 -j $MAX_PARALLEL_JOBS --halt soon,fail=1 --line-buffer \
  --tagstring '|job#{#} of {= $_=total_jobs() =} s#{%}|' load_csv '{}'
