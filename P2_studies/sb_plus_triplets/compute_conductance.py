#!/usr/bin/env python3
"""
@author: Shreya Chandrasekharan

This script computes conductance for given clusters. 

Argument(s): rootdir               - The directory where all cluster-scp list information is stored
             cluster_type          - The type of cluster to process - (shuffled, unshuffled, graclus)
             
Output:      conductance_x5        - Final data frame of complete conductance computation
"""

import pandas as pd
from sys import argv

rootdir = '/erniedev_data3/sb_plus_triplets/mcl'
cluster_type = argv[1]

if cluster_type == 'unshuffled':
    cluster_path = rootdir +  "/triplets_I20/"  + "dump.triplets_cited.mci.I20.csv"
    cluster_data = pd.read_csv(cluster_path)
elif cluster_type == 'shuffled':
    cluster_path = rootdir +  "/triplets_I20/"  + "dump.triplets_cited.shuffled_1million.I20.csv" 
    cluster_data = pd.read_csv(cluster_path)
elif cluster_type == 'graclus':
    graclus_coded_cluster_num_path = rootdir + "/output_I20/" + '/graclus_triplets_cited.csv.part.6021'
    graclus_coded_cluster_num = pd.read_csv(glob(graclus_coded_cluster_num_path)[0], header=None)
    graclus_coded_cluster_num.columns = ['cluster_no']
    graclus_coded_cluster_num['citing_id'] = range(1, len(graclus_coded_cluster_num)+1)
    graclus_nodes_path = rootdir + "/output_I20/" + "/graclus_coded_triplets_cited.csv"
    graclus_nodes = pd.read_csv(graclus_nodes_path)
    graclus_clusters = graclus_nodes.merge(graclus_coded_cluster_num)
    graclus_clusters = graclus_clusters.astype({'citing':object, 'citing_id':object, 'cluster_no':object}) 
    cluster_data = graclus_clusters[['citing', 'cluster_no']].rename(columns={'citing':'scp'})

nodes_data_name = rootdir +  "/triplets_I20/"  + "triplets_cited.csv"
nodes_data = pd.read_csv(nodes_data_name)

conductance_data = nodes_data.merge(cluster_data, left_on='citing', right_on='scp', how='inner').rename(columns={'cluster_no':'citing_cluster'}).merge(cluster_data, left_on='cited', right_on='scp', how='inner').rename(columns={'cluster_no':'cited_cluster'})

conductance_data = conductance_data[['citing', 'cited', 'citing_cluster', 'cited_cluster']]

conductance_counts_data = cluster_data.groupby('cluster_no', as_index=False).agg('count').rename(columns={'cluster_no':'cluster', 'scp':'cluster_counts'})

conductance_x1 = conductance_data[conductance_data.cited_cluster != conductance_data.citing_cluster][['citing', 'citing_cluster']].groupby('citing_cluster', as_index=False).agg('count').rename(columns = {'citing': 'ext_out'})
conductance_x2 = conductance_data[conductance_data.cited_cluster != conductance_data.citing_cluster][['cited', 'cited_cluster']].groupby('cited_cluster', as_index=False).agg('count').rename(columns = {'cited': 'ext_in'})
conductance_x3 = conductance_data[conductance_data.cited_cluster == conductance_data.citing_cluster][['citing', 'cited_cluster']].groupby('cited_cluster', as_index=False).agg('count').rename(columns = {'citing': 'int_edges'})

conductance_x1_clusters = conductance_counts_data.merge(conductance_x1, left_on = 'cluster', right_on = 'citing_cluster', how = 'left')[['cluster', 'ext_out']]
conductance_x1_clusters = conductance_x1_clusters.fillna(0)
conductance_x2_clusters = conductance_counts_data.merge(conductance_x2, left_on = 'cluster', right_on = 'cited_cluster', how = 'left')[['cluster', 'ext_in']]
conductance_x2_clusters = conductance_x2_clusters.fillna(0)
conductance_x3_clusters = conductance_counts_data.merge(conductance_x3, left_on = 'cluster', right_on = 'cited_cluster', how = 'left')[['cluster', 'int_edges', 'cluster_counts']]
conductance_x3_clusters = conductance_x3_clusters.fillna(0)

conductance_x4 = conductance_x1_clusters.merge(conductance_x2_clusters, left_on='cluster', right_on='cluster', how = 'inner')
conductance_x5 = conductance_x4.merge(conductance_x3_clusters, left_on='cluster', right_on='cluster')
conductance_x5['boundary'] = conductance_x5['ext_in'] + conductance_x5['ext_out']
conductance_x5['volume'] = conductance_x5['ext_in'] + conductance_x5['ext_out'] + 2*conductance_x5['int_edges']
conductance_x5['two_m'] = conductance_data.shape[0]*2
conductance_x5['alt_denom'] = conductance_x5['two_m'] - conductance_x5['volume']
conductance_x5['denom'] = conductance_x5[['alt_denom', 'volume']].min(axis=1)
conductance_x5['conductance'] = round((conductance_x5['boundary']/conductance_x5['denom']), 3)

save_name = rootdir + "/output_I20/" +   "triplets_cited"  + "_conductance_" + cluster_type + ".csv"
conductance_x5.to_csv(save_name, index = None, header=True, encoding='utf-8')

print("All completed.")

