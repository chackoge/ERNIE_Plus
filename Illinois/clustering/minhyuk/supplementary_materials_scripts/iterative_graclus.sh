FINAL_OUTPUT_PREFIX="<Final output folder>"
CLUSTERINGS_FOLDER="<Output folder to each iteration's clusterings>"
CLUSTERING_OUTPUT_PREFIX="${CLUSTERINGS_FOLDER}"
SAVE_FOR_LATER_PREFIX="<Output folder to contain the clusters deemed to be included in the final clusterings>"
INPUT_NETWORK="<Input network>"
local_search="<integer local search parameter at least 0 for graclus>"
k="<integer at least 0 for k-validity checks>"
p=-1
NUM_ITERATIONS="<Number of iterations>"

for iteration in $(seq 1 ${NUM_ITERATIONS})
do
    PREVIOUS_CLUSTERING_FILE="${CLUSTERING_OUTPUT_PREFIX}/clustering_$((${iteration} - 1)).clustering"
    CURRENT_CLUSTERING_FILE_PREFIX="${CLUSTERING_OUTPUT_PREFIX}/clustering_${iteration}"
    TEMP_FILE_PREFIX="auxillary_files_iteration_${iteration}"
    mkdir ${TEMP_FILE_PREFIX}
    python -m python_scripts.cluster_processing_scripts.single_graclus --clustering ${PREVIOUS_CLUSTERING_FILE} --network ${INPUT_NETWORK} --output-prefix ${TEMP_FILE_PREFIX} --local-search ${local_search}
    mv ${TEMP_FILE_PREFIX}/single_graclus.clustering ${TEMP_FILE_PREFIX}/full_clustering_${iteration}.clustering
    python parsing_clusters.py -e ${INPUT_NETWORK} -o ${TEMP_FILE_PREFIX}/clustering_${iteration}.node_comma_cluster.clustering -c ${TEMP_FILE_PREFIX}/full_clustering_${iteration}.clustering -k ${k} -p ${p}
    python -m python_scripts.cluster_processing_scripts.convert_to_cluster_id_format --clustering-output ${TEMP_FILE_PREFIX}/clustering_${iteration}.node_comma_cluster.clustering --output-prefix ${CURRENT_CLUSTERING_FILE_PREFIX}.clustering --cluster-method parsing_clusters
    python -m python_scripts.cluster_processing_scripts.generate_save_for_later --previous-clustering ${PREVIOUS_CLUSTERING_FILE} --current-clustering ${CURRENT_CLUSTERING_FILE_PREFIX}.clustering --output-prefix ${TEMP_FILE_PREFIX} --iteration-number ${iteration}
    mv ${TEMP_FILE_PREFIX}/save_for_later_${iteration}.clustering ${SAVE_FOR_LATER_PREFIX}/save_for_later_${iteration}.clustering
done
# if the iteration ends early, meaning the output clustering of that iteration is empty, then just modify the script
# such that the clustering-folder argument only contains the clusterings to be merged
mv ${CLUSTERING_OUTPUT_PREFIX}/clustering_${NUM_ITERATIONS}.clustering ${SAVE_FOR_LATER_PREFIX}/
python -m python_scripts.cluster_processing_scripts.merge_clusterings --clustering-folder ${SAVE_FOR_LATER_PREFIX} --output-prefix ${FINAL_OUTPUT_PREFIX} 2> ${FINAL_OUTPUT_PREFIX}/merge_clusterings.err 1> ${FINAL_OUTPUT_PREFIX}/merge_clusterings.out
