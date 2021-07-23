#!/bin/bash
# this script is a wrapper around leiden that is instaleld on valhalla
SIZE="full"

OUTPUT_PREFIX="./${SIZE}/"
OUTPUT_FILE="./${SIZE}/leiden.clusters"
INPUT_NETWORK="/home/minhyuk2/git_repos/ERNIE_Plus/Illinois/clustering/minhyuk/kalluri/${SIZE}/kalluri_sample_network.integer_label.${SIZE}.tsv"
RESOLUTION="0.2"

/usr/bin/time -v java -cp /srv/local/shared/external/leiden/networkanalysis-1.1.0/leiden.jar nl.cwts.networkanalysis.run.RunNetworkClustering -r ${RESOLUTION} -o ${OUTPUT_FILE} ${INPUT_NETWORK} 2> ${OUTPUT_PREFIX}/leiden_${SIZE}.err 1> ${OUTPUT_PREFIX}/leiden_${SIZE}.out
