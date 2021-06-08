# Input file is kalluri_sample_network.csv
# Convert to tsv
sed -E 's/("([^"]*)")?,/\2\t/g' kalluri_sample_network.csv > kalluri_sample_network.tsv
# Remove header line
sed -i '1d' kalluri_sample_network.csv.tsv
# Convert to undirected graph in matrix format
mcxload --stream-mirror -abc kalluri_sample_network.tsv -o kalluri_sample_network.mci -write-tab kalluri_sample_network.tab
# Run MCL with IF 1.0 DONT RUN WITH 1.0
mcl kalluri_sample_network.mci -I 1.0
# Write output to dump.aibs.mci.I14 using labels from .tab file
mcxdump -icl out.kalluri_sample_network.mci.I10 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I10

# need to write a loop but..

mcl kalluri_sample_network.mci -I 1.2
mcl kalluri_sample_network.mci -I 1.4
mcl kalluri_sample_network.mci -I 1.6
mcl kalluri_sample_network.mci -I 1.8
mcl kalluri_sample_network.mci -I 2.0

mcxdump -icl out.kalluri_sample_network.mci.I10 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I10
mcxdump -icl out.kalluri_sample_network.mci.I12 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I12
mcxdump -icl out.kalluri_sample_network.mci.I14 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I14
mcxdump -icl out.kalluri_sample_network.mci.I16 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I16
mcxdump -icl out.kalluri_sample_network.mci.I18 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I18
mcxdump -icl out.kalluri_sample_network.mci.I20 -tabr kalluri_sample_network.tab -o dump.kalluri_sample_network.mci.I20


