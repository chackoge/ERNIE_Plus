#!/usr/bin/env bash
if [[ $1 == "-h" ]]; then
  cat <<'HEREDOC'
NAME

  neo4j_bulk_import.sh -- calculate graph metrics

SYNOPSIS

  neo4j_calc_metrics.sh
  neo4j_calc_metrics.sh -h: display this help

DESCRIPTION

  Calculate metrics: PageRank, Betweenness Centrality, Closeness Centrality

HEREDOC
  exit 1
fi

set -e
set -o pipefail

echo "Calculating metrics"
cypher-shell <<'HEREDOC'
// Calculate and store PageRank
CALL algo.pageRank()
YIELD nodes, iterations, loadMillis, computeMillis, writeMillis, dampingFactor, write, writeProperty;

// Calculate and store Betweenness Centrality
CALL algo.betweenness(null, null, {writeProperty: 'betweenness'})
YIELD nodes, minCentrality, maxCentrality, sumCentrality, loadMillis, computeMillis, writeMillis;

// Calculate and store Closeness Centrality
CALL algo.closeness(null, null, {writeProperty: 'closeness'})
YIELD nodes, loadMillis, computeMillis, writeMillis;

// PageRank statistics
MATCH (n)
RETURN apoc.agg.statistics(n.pagerank);
HEREDOC

#TBD Running into `Failed to invoke procedure `algo.pageRank`: Caused by: java.lang.NullPointerException`
#parallel --null --halt soon,fail=1 --line-buffer --tagstring '|job#{#} s#{%}|' 'echo {} | cypher-shell' ::: \
#  "// Calculate and store PageRank
#  CALL algo.pageRank()
#  YIELD nodes, iterations, loadMillis, computeMillis, writeMillis, dampingFactor, write, writeProperty;" \
#  "// Calculate and store Betweenness Centrality
#  CALL algo.betweenness(null, null, {writeProperty: 'betweenness'})
#  YIELD nodes, minCentrality, maxCentrality, sumCentrality, loadMillis, computeMillis, writeMillis;" \
#  "// Calculate and store Closeness Centrality
#  CALL algo.closeness(null, null, {writeProperty: 'closeness'})
#  YIELD nodes, loadMillis, computeMillis, writeMillis;" \
#  "CREATE INDEX ON :Publication(node_id);"
#
#cypher-shell <<'HEREDOC'
#// PageRank statistics
#MATCH (n)
#RETURN apoc.agg.statistics(n.pagerank);
#HEREDOC