#!/usr/bin/env bash
if [ "$POSIXLY_CORRECT" = "y" ]; then
  echo "This script is not designed for POSIX mode" >&2
  exit 1
fi

if [[ ! $BASH ]]; then
  echo "This script is designed for Bash only" >&2
  exit 1
fi

set -e
set -o pipefail

readonly SCRIPT_VER=4.5.1

# Remove the longest `*/` prefix
readonly SCRIPT_FULL_NAME="${0##*/}"
max_parallel_jobs=1

usage() {
  cat <<HEREDOC
NAME

    $SCRIPT_FULL_NAME -- load OpenCitations Index data from CSVs in parallel

SYNOPSIS

    $SCRIPT_FULL_NAME [-c] [-j parallel_jobs] [-s batch_max_records] [-d data_dir]
    $SCRIPT_FULL_NAME -h: display this help

DESCRIPTION

    Append OpenCitations Index data from CSVs in parallel. Optionally, split input files into batches.
    The script can resume an execution after an error.

    The following options are available:

    -d data_dir           directory with Open Citations *.csv files to process (non-recursively) [DEFAULT: .]
                          The CSV files in it must be readable by the executing user.

    -c                    clean (remove) loaded CSVs: recommended to simplify error recovery
                          The CSV files in this case must be writeable by the executing user.

    -j parallel_jobs      maximum number of parallel jobs [DEFAULT: $max_parallel_jobs]

    -s batch_max_records  split and process each CSV in batches up to this maximum number of records

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

v$SCRIPT_VER
HEREDOC
  exit 1
}

if [[ $1 == "-h" ]]; then
  usage
fi

DATA_DIR=.
# If a colon follows a character, the option is expected to have an argument
while getopts cj:s:d:h OPT; do
  case "$OPT" in
  c)
    declare -rx REMOVE_LOADED=true
    ;;
  j)
    max_parallel_jobs=$OPTARG
    ;;
  s)
    declare -rx BATCH_SIZE=$OPTARG
    ;;
  d)
    readonly DATA_DIR="$OPTARG"
    ;;
  *) # -h or `?`: an unknown option
    usage
    ;;
  esac
done

########################################################################################################################
# Print basic info about the running script and parameters
#
# Globals:
#   $SCRIPT_VER
########################################################################################################################
hello() {
  local exec_sh
  exec_sh=$(ps -p "$$" -o comm=)
  if [[ "$exec_sh" != /* ]]; then
    # Shell filename without the path: `script.sh` (= `/usr/bin/env bash script.sh`) or `shell script.sh` execution

    # Suffix after the first '-', if any. Login shell process names start with `-`, e.g. `-bash`.
    local -r EXEC_SH_NAME=${exec_sh#*-}

    # The parent, e.g., login, interactive shell, finds the subshell to execute on its PATH. The following is the
    # best guess assuming that this subshell (non-login, non-interactive) PATH is the same.
    exec_sh="$(which "$EXEC_SH_NAME") (?)"
  fi
  printf '\n[%s] %s@%s %s> [%s] %s [v%s]' "$(date +'%T %Z')" "$(id -un)" "${HOSTNAME}" "${PWD}" "${exec_sh}" "$0" \
    "$SCRIPT_VER"
  if (($# > 0)); then
    printf ' '
    printf '"%s" ' "$@"
  fi
  printf '\n\n'
}

hello "$@"

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
readonly ABSOLUTE_SCRIPT_DIR=$(cd "${SCRIPT_DIR}" && pwd)

########################################################################################################################
# Loads a single header-less CSV batch of Open Citations.
# Executed in a subshell by `parallel`.
#
# Arguments:
#   $1 absolute CSV filename
########################################################################################################################
load_csv() {
  set -e
  set -o pipefail
  local -r ABSOLUTE_FILE_PATH=$1
  echo "Processing ${ABSOLUTE_FILE_PATH} ..."

  if [[ $BATCH_SIZE ]]; then
    local -r HEADERS=OFF
  else
    local -r HEADERS=MATCH
  fi
  # language=PostgresPLSQL
  psql -v ON_ERROR_STOP=on <<HEREDOC
      COPY stg_open_citations (oci, citing, cited, creation, timespan, journal_sc, author_sc)
      FROM '${ABSOLUTE_FILE_PATH}' (FORMAT CSV, HEADER $HEADERS);
HEREDOC

  echo "Loaded ${ABSOLUTE_FILE_PATH}"
  if [[ $REMOVE_LOADED ]]; then
    rm -v "${ABSOLUTE_FILE_PATH}"
  fi
}
export -f load_csv

echo "Starting data load: appending all records to existing OpenCitations Index data."

psql -f "$ABSOLUTE_SCRIPT_DIR/load-open-citations-index-pre.sql"

cd "$DATA_DIR"
if [[ $BATCH_SIZE ]]; then
  if [[ ! -d batches ]]; then
    mkdir -p batches
    # shellcheck disable=SC2016 # `--tagstring` tokens are expanded by GNU `parallel`
    find . -maxdepth 1 -name '*.csv' -type f -print0 | parallel -0 -j "$max_parallel_jobs" --halt soon,fail=1 \
        --verbose --line-buffer --tagstring '|job #{#} of {= $_=total_jobs() =} slot #{%}|' \
        "tail -n +2 {} | split --lines=$BATCH_SIZE --suffix-length=4 --numeric-suffixes=1 --elide-empty-files \
          --additional-suffix=.csv - batches/{}.part"
  fi
  cd batches
fi

# Load files. If the load fails, the process can nbe resumed here on the remaining files.
# Piping to `parallel` is done by design here to handle a large number of files potentially
# shellcheck disable=SC2016 # `--tagstring` tokens are expanded by GNU `parallel`
find ~+ -maxdepth 1 -type f -name '*.csv' -print0 | parallel -0 -j "$max_parallel_jobs" --halt soon,fail=1 \
    --line-buffer --tagstring '|job #{#} of {= $_=total_jobs() =} slot #{%}|' load_csv '{}'
cd "$DATA_DIR"

# Successfully loaded all input files
rm -rf batches
if [[ $REMOVE_LOADED && $BATCH_SIZE ]]; then
  # Remove original files (they were split into batches and left over)
  rm -fv -- *.csv
fi

psql -f "$ABSOLUTE_SCRIPT_DIR/load-open-citations-index-post.sql"
