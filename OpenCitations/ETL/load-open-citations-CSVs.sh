#!/usr/bin/env bash
set -e
set -o pipefail

# When the # of jobs >= 74 Postgres 12 gets oveloaded and crashes with the `DETAIL:  The postmaster has commanded this
# server process to roll back the current transaction and exit, because another server process exited abnormally and
# possibly corrupted shared memory.` error. The limit should be in the [4..74) range with Postgres tuned as it is now.
readonly MAX_PARALLEL_JOBS=64

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
  psql -v ON_ERROR_STOP=on -v "file=${absolute_file_path}" << 'HEREDOC'
    COPY stg_open_citations(oci, citing, cited, creation, timespan, journal_sc, author_sc)
    FROM :'file' (FORMAT CSV, HEADER ON);
HEREDOC

  echo "Loaded ${file}"
}
export -f load_csv

echo "Starting data load: appending all records to existing Open Citations data."

# Piping `ls` to `parallel` is done by design here: handling potentially a large number of files
# shellcheck disable=SC2016 # `--tagstring` tokens are expanded by GNU `parallel`
find . -maxdepth 1 -type f -name '*.csv' -print0 | parallel -0 -j $MAX_PARALLEL_JOBS --halt soon,fail=1 --line-buffer \
    --tagstring '|job#{#} of {= $_=total_jobs() =} s#{%}|' load_csv '{}'


