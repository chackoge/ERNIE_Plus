#!/bin/bash
SIZE="full"

OUTPUT_PREFIX="./${SIZE}/"
OUTPUT_FILE="./${SIZE}/leiden.clusters"
INPUT_NETWORK="/home/minhyuk2/git_repos/ERNIE_Plus/Illinois/clustering/minhyuk/kalluri/${SIZE}/kalluri_sample_network.integer_label.${SIZE}.tsv"
RESOLUTION="0.2"

# TODO: update the leiden installation since this is only on gypsy
/usr/bin/time -v java -cp /usr/local/bin/networkanalysis-1.1.0.jar nl.cwts.networkanalysis.run.RunNetworkClustering -r ${RESOLUTION} -o ${OUTPUT_FILE} ${INPUT_NETWORK} 2> ${OUTPUT_PREFIX}/leiden_${SIZE}.err 1> ${OUTPUT_PREFIX}/leiden_${SIZE}.out
