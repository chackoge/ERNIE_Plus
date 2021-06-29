# Input file is kalluri_sample_network.csv
# Convert to tsv
sed -E 's/("([^"]*)")?,/\2\t/g' ../kalluri_sample_network.csv > ./kalluri_sample_network.tsv
# Remove header line
sed -i '1d' ./kalluri_sample_network.csv.tsv
# Convert to undirected graph in matrix format
mcxload --stream-mirror -abc ./kalluri_sample_network.tsv -o ./kalluri_sample_network.mci -write-tab ./kalluri_sample_network.tab
# Run MCL with IF 1.0 DONT RUN WITH 1.0
# mcl kalluri_sample_network.mci -I 1.0
# Write output to dump.aibs.mci.I14 using labels from .tab file
# mcxdump -icl out.kalluri_sample_network.mci.I10 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I10

# need to write a loop but..

mcl kalluri_sample_network.mci -I 1.2
mcl kalluri_sample_network.mci -I 2.0
mcl kalluri_sample_network.mci -I 4.0
mcl kalluri_sample_network.mci -I 6.0

echo "Starting 1.2"
mcxdump -icl out.kalluri_sample_network.mci.I12 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I12
echo "Starting 2.0"
mcxdump -icl out.kalluri_sample_network.mci.I20 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I20
echo "Starting 4.0"
mcxdump -icl out.kalluri_sample_network.mci.I40 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I40
echo "Starting 6.0"
mcxdump -icl out.kalluri_sample_network.mci.I60 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I60
echo "done"
