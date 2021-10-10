#!/usr/bin/env bash

usage() {
  cat <<'HEREDOC'
NAME

    neo4j-switch-db.sh -- switch Neo4j 4 default DB

SYNOPSIS

    neo4j-switch-db.sh [-r] neo4j_db
    neo4j-switch-db.sh -h: display this help

DESCRIPTION

    Switch Neo4j 4 default DB.

    The following options are available:

    -r            Restart Neo4j. This also would activate a new default DB.
                  Executing user must be able to run `systemctl`: either run the script under `root` or enable this
                  via PolKit.

ENVIRONMENT

    * Neo4j must be set up to permit configuration update for the executing user: either run under `neo4j` or set up
    `neo4j` group permissions:
      * `sudo chmod -R g+w /etc/neo4j`

v3.0                                   September 2021                                  Created by Dmitriy "DK" Korobskiy
HEREDOC
  exit 1
}

set -e
set -o pipefail

# If a character is followed by a colon, the option is expected to have an argument
while getopts rh OPT; do
  case "$OPT" in
    r)
      readonly RESTART=true
      ;;
    *) # -h or `?`: an unknown option
      usage
      ;;
  esac
done
shift $((OPTIND - 1))

readonly DB_NAME="$1"
[[ $DB_NAME == "" ]] && usage

# `${USER:-${USERNAME:-${LOGNAME}}}` might be not available inside Docker containers
echo -e "\n# neo4j-switch-db.sh: running under $(whoami)@${HOSTNAME} in ${PWD} #\n"

if ! command -v cypher-shell >/dev/null; then
  echo "Please install Neo4j"
  exit 1
fi

sed --in-place --expression="s/^dbms.default_database=.*/dbms.default_database=${DB_NAME}/" /etc/neo4j/neo4j.conf
echo "The default database = \`$DB_NAME\`"

if [[ $RESTART ]]; then
  echo "Restarting Neo4j with a new default database..."
  systemctl restart neo4j

  declare -i time_limit_s=30
  echo "Waiting for the service to become active up to ${time_limit_s} seconds ..."
  # Ping Neo4j. Even if a service is active it might not be responding yet.
  while ! cypher-shell "CALL dbms.components()" 2>/dev/null; do
    if ((time_limit_s-- == 0)); then
      echo "ERROR: Neo4j with the default DB ${DB_NAME} failed to start." >&2
      exit 2
    fi
    sleep 1
  done
else
  echo "NOTE: restart the service to activate the new default database"
fi