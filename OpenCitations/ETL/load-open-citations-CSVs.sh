#!/usr/bin/env bash
set -e
set -o pipefail

readonly VER=4.1.0

# Remove the longest `*/` prefix
readonly SCRIPT_FULL_NAME="${0##*/}"

# `\\copy` of large Open Citations CSVs (1.5-1.8 G) consumes a lot of memory, e.g. ≈ 100 G for 32 jobs.
# When the # of jobs is too large the entire machine might get overloaded.
max_parallel_jobs=1
chunk_size=100000

usage() {
  cat <<HEREDOC
NAME

    $SCRIPT_FULL_NAME -- load Open Citations CSVs in parallel

SYNOPSIS

    $SCRIPT_FULL_NAME [-c] [-j parallel_jobs] [-s chunk_size] [data_directory]
    $SCRIPT_FULL_NAME -h: display this help

DESCRIPTION

    Load Open Citations CSVs in parallel. Split input files into chunks.

    The following options are available:

    data_directory  directory with Open Citations *.csv files to process (non-recursively) [DEFAULT: .]
                    The CSV files in it must be readable by the executing user.

    -c              clean (remove) loaded CSVs: recommended to simplify error recovery
                    The CSV files in this case must be writeable by the executing user.

    -j              maximum number of parallel jobs [DEFAULT: $max_parallel_jobs]

    -s              maximum number of lines (citations) per chunk and transaction [DEFAULT: $chunk_size]

ENVIRONMENT

    * GNU \`parallel\` utility is required.

    * Local Postgres must have a user with the name = {OS executing user} and a Postgres role with these privileges:
      * \`pg_read_server_files\`
      * INSERT on \`public.*open_citations*\` tables and views
      * EXECUTE on \`public.to_date()\` and \`public.to_interval()\` functions
      * CREATE on SCHEMA \`public\`

EXIT STATUS
    The process stops gracefully on the first error.

    The $SCRIPT_FULL_NAME utility exits with one of the following values:

    0     All files have been successfully loaded
    1-100 The number of files failed to load
    255   Usage help is requested or invalid options

v$VER
HEREDOC
  exit 255
}


# If a colon follows a character, the option is expected to have an argument
while getopts cj:s:h OPT; do
  case "$OPT" in
  c)
    declare -rx REMOVE_LOADED=true
    ;;
  j)
    max_parallel_jobs=$OPTARG
    ;;
  s)
    chunk_size=$OPTARG
    ;;
  *) # -h or `?`: an unknown option
    usage
    ;;
  esac
done
echo -e "\n# \`$0${*+ }$*\` v$VER: run by \`${USER:-${USERNAME:-${LOGNAME:-UID #$UID}}}@${HOSTNAME}\` in \`${PWD}\` #\n"
shift $((OPTIND - 1))

# Process positional parameters
readonly DATA_DIR="${1:-.}"

if ! command -v parallel >/dev/null; then
  echo "Please install GNU parallel"
  exit 1
fi

readonly SCRIPT_FILENAME=$0
if [[ "${SCRIPT_FILENAME}" != */* ]]; then
  SCRIPT_FILENAME=./${SCRIPT_FILENAME}
fi
# Remove shortest /* suffix
readonly SCRIPT_DIR=${SCRIPT_FILENAME%/*}

load_csv() {
  set -e
  set -o pipefail
  local csv_file=$1
  echo "Processing ${csv_file} ..."
  # Remove longest */ prefix
  local name_with_ext=${csv_file##*/}

  cd chunks
  # Strip header and split into header-less chunks
  tail -n +2 "../${name_with_ext}" | split --lines="$chunk_size" --numeric-suffixes=1 --elide-empty-files \
    --additional-suffix=.csv --verbose - "${name_with_ext}.part"

  local absolute_chunk_dir
  absolute_chunk_dir=$(pwd)
  for csv_chunk in "${name_with_ext}".part*; do
    absolute_file_path="${absolute_chunk_dir}/${csv_chunk}"
    # language=PostgresPLSQL
    psql -v ON_ERROR_STOP=on <<HEREDOC
      COPY stg_open_citations (oci, citing, cited, creation, timespan, journal_sc, author_sc)
      FROM '${absolute_file_path}' (FORMAT CSV, HEADER OFF);
HEREDOC
  done
  cd ..

  echo "Loaded ${csv_file}"
  if [[ $REMOVE_LOADED ]]; then
    rm -v "${csv_file}"
  fi
}
export -f load_csv

echo "Starting data load: appending all records to existing Open Citations data."

psql -f "$SCRIPT_DIR/pre_processing.sql"

cd "$DATA_DIR"
mkdir -p chunks
# Piping to `parallel` is done by design here to handle a large number of files potentially
# shellcheck disable=SC2016 # `--tagstring` tokens are expanded by GNU `parallel`
find . -maxdepth 1 -type f -name '*.csv' -print0 |
  parallel -0 -j "$max_parallel_jobs" --halt soon,fail=1 --line-buffer \
    --tagstring '|job#{#} of {= $_=total_jobs() =} s#{%}|' load_csv '{}'
cd -

psql -f "$SCRIPT_DIR/post_processing.sql"

# shellcheck disable=SC2064 # DATA_DIR is defined once and available at the point of trap definition
trap "rm -rf $DATA_DIR/chunks" EXIT
