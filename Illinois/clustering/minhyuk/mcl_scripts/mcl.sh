# Input file is kalluri_sample_network.csv
# Convert to tsv
DATA_ROOT="./"
DATASET_NAME="exosome_1900_1989_citing_cited_network"
DATASET_PATH="${DATA_ROOT}${DATASET_NAME}"
ORIGINAL_CSV="/srv/shared/external/Dimensions/no_authors_datasets_minhyuk2/exosome_1900_1989/citing_cited_network.csv"
DESTINATION_TSV="${DATASET_PATH}.tsv"
OUTPUT_MCI="${DATASET_PATH}.mci"
OUTPUT_TAB="${DATASET_PATH}.tab"

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

# Run MCL with IF 1.0 DONT RUN WITH 1.0
# mcl kalluri_sample_network.mci -I 1.0
# Write output to dump.aibs.mci.I14 using labels from .tab file
# mcxdump -icl out.kalluri_sample_network.mci.I10 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I10

# need to write a loop but..

/srv/shared/external/mcl-14-137/bin/mcl ${OUTPUT_MCI} -I 1.2
# /srv/shared/external/mcl-14-137/bin/mcl ${OUTPUT_MCI} -I 2.0
# /srv/shared/external/mcl-14-137/bin/mcl ${OUTPUT_MCI} -I 4.0
# /srv/shared/external/mcl-14-137/bin/mcl ${OUTPUT_MCI} -I 6.0

# echo "Starting 1.2"
# /srv/shared/external/mcl-14-137/bin/mcxdump -icl out.${DATASET_NAME}.I12 -tabr ${OUTPUT_TAB} -o dump.${OUTPUT_MCI}.I12
#echo "Starting 2.0"
#mcxdump -icl out.kalluri_sample_network.mci.I20 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I20
#echo "Starting 4.0"
#mcxdump -icl out.kalluri_sample_network.mci.I40 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I40
#echo "Starting 6.0"
#mcxdump -icl out.kalluri_sample_network.mci.I60 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I60
echo "done"
