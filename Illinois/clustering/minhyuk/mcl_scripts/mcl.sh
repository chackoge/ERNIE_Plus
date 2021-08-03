#!/bin/bash
# This script runs the mcl installed on valhalla given the dataset location and original edge list network in csv format

DATA_ROOT="<DATASET FILE LOCATION>"
DATASET_NAME="<DATASET NAME>"
DATASET_PATH="${DATA_ROOT}${DATASET_NAME}"
ORIGINAL_CSV="<ORIGINAL CSV FILE>"
DESTINATION_TSV="<OUTPUT TSV LOCATION>.tsv"
OUTPUT_MCI="<OUTPUT MCI LOCATION>.mci"
OUTPUT_TAB="<OUTPUT TAB LOCATIAN>.tab"

if [ ! -f ${DESTINATION_TSV} ]; then
    echo "converting csv to tsv and stripping the header"
    sed -E 's/("([^"]*)")?,/\2\t/g' ${ORIGINAL_CSV} > ${DESTINATION_TSV}
    # Remove header line
    sed -i '1d' ${DESTINATION_TSV}
fi

# Convert to undirected graph in matrix format
if [ ! -f ${OUTPUT_TAB} ]; then
    /srv/shared/external/mcl-14-137/bin/mcxload --stream-mirror -abc ${DESTINATION_TSV} -o ${OUTPUT_MCI} -write-tab ${OUTPUT_TAB}
fi

# Run MCL with DONT RUN WITH 1.0
if [ ! -f out.${DATASET_NAME}.I12 ]; then
    echo "Starting 1.2"
    /srv/shared/external/mcl-14-137/bin/mcl ${OUTPUT_MCI} -I 1.2 -o out.${DATASET_NAME}.I12
fi

if [ ! -f dump.${DATASET_NAME}.I12 ]; then
    /srv/shared/external/mcl-14-137/bin/mcxdump -icl out.${DATASET_NAME}.I12 -tabr ${OUTPUT_TAB} -o dump.${DATASET_NAME}.I12
fi

if [ ! -f dump.${DATASET_NAME}.I12.csv ]; then
    Rscript ./post_process.R # this takes in all files that match dump.*
fi

echo "done"
