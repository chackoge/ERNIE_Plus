#!/usr/bin/env bash
if [[ $1 == "-h" || $# -lt 1 ]]; then
  cat <<'HEREDOC'
NAME
  neo4j-switch-db.sh -- switches Neo4j 4 default DB and restarts Neo4j. This also would activate a new imported DB.

SYNOPSIS
  neo4j-switch-db.sh neo4j_db
  neo4j-switch-db.sh -h: display this help

ENVIRONMENT
  # Current user must be a sudoer
HEREDOC
  exit 1
fi

set -e
set -o pipefail

# Get a script directory, same as by $(dirname $0)
#script_dir=${0%/*}
#absolute_script_dir=$(cd "${script_dir}" && pwd)
#work_dir=${1:-${absolute_script_dir}/build} # $1 with the default
#if [[ ! -d "${work_dir}" ]]; then
#  mkdir "${work_dir}"
#  chmod g+w "${work_dir}"
#fi
#cd "${work_dir}"
echo -e "\n## Running under ${USER}@${HOSTNAME} at ${PWD} ##\n"

if ! command -v cypher-shell >/dev/null; then
  echo "Please install Neo4j"
  exit 1
fi

readonly DB_NAME="$1"

# region Hide password from the output
sudo -u neo4j bash -c "set -xe
  sed --in-place --expression='s/^dbms.default_database=.*/dbms.default_database=${DB_NAME}/' /etc/neo4j/neo4j.conf"

echo "Restarting Neo4j with a new default database ..."
sudo systemctl restart neo4j

declare -i time_limit_s=30
echo "Waiting for the service to become active up to ${time_limit_s} seconds ..."
# Ping Neo4j. Even if a service is active it might not be responding yet.
while ! cypher-shell "CALL dbms.components()" 2>/dev/null; do
  if ((time_limit_s-- == 0)); then
    echo "ERROR: The DB ${DB_NAME} failed to start." >&2
    exit 2
  fi
  sleep 1
done
# endregion