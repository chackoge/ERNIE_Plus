import pandas as pd
from sqlalchemy import create_engine
from sys import argv
from collections import Counter

schema = "theta_plus"
user_name = argv[1]
password = argv[2]
start_cluster_num = argv[3]

sql_scheme = 'postgresql://' + user_name + ':' + password + '@localhost:5432/ernie'
engine = create_engine(sql_scheme)

cluster_query = """SELECT cluster_no
FROM theta_plus.imm1985_1995_all_merged_mcl
ORDER BY cluster_no;"""

clusters = pd.read_sql(cluster_query, con=engine)
clusters_list = clusters['cluster_no']#[(clusters['cluster_size'] >= 30) & (clusters['cluster_size'] <= 350)].astype(int).tolist()

external_cluster_degrees_query = """SELECT cluster_no, sum(ext_cluster_total_degrees) as ext_cluster_total_degrees
FROM theta_plus.imm1985_1995_external_cluster_degrees_mcl GROUP BY cluster_no ORDER BY cluster_no;"""

external_cluster_degrees = pd.read_sql(external_cluster_degrees_query, con=engine)

if start_cluster_num == "first":
    start_num = 0
else:                     
    start_num = clusters_list.index(int(start_cluster_num))

for cluster_num in clusters_list[start_num:]:

    citing_cited_query = """
        SELECT cslu1.cluster_no as citing_cluster, ccu.citing, ccu.cited, cslu2.cluster_no as cited_cluster
        FROM theta_plus.imm1985_1995_citing_cited ccu
        JOIN (SELECT cslu.*
              FROM theta_plus.imm1985_1995_cluster_scp_list_mcl cslu
              JOIN theta_plus.imm1985_1995_article_score_unshuffled asu ON asu.scp = cslu.scp
              WHERE asu.article_score >= 1) cslu1 ON cslu1.scp = ccu.citing
        JOIN (SELECT cslu.*
              FROM theta_plus.imm1985_1995_cluster_scp_list_mcl cslu
              JOIN theta_plus.imm1985_1995_article_score_unshuffled asu ON asu.scp = cslu.scp
              WHERE asu.article_score >= 1) cslu2 ON cslu2.scp = ccu.cited
        WHERE cslu1.cluster_no=""" +str(cluster_num)+ """ AND cslu1.cluster_no!=cslu2.cluster_no
        UNION
        SELECT cslu1.cluster_no as citing_cluster, ccu.citing, ccu.cited, cslu2.cluster_no as cited_cluster
        FROM theta_plus.imm1985_1995_citing_cited ccu
        JOIN (SELECT cslu.*
              FROM theta_plus.imm1985_1995_cluster_scp_list_mcl cslu
              JOIN theta_plus.imm1985_1995_article_score_unshuffled asu ON asu.scp = cslu.scp
              WHERE asu.article_score >= 1) cslu1 ON cslu1.scp = ccu.citing
        JOIN (SELECT cslu.*
              FROM theta_plus.imm1985_1995_cluster_scp_list_mcl cslu
              JOIN theta_plus.imm1985_1995_article_score_unshuffled asu ON asu.scp = cslu.scp
              WHERE asu.article_score >= 1) cslu2 ON cslu2.scp = ccu.cited
        WHERE cslu2.cluster_no=""" +str(cluster_num)+ """ AND cslu1.cluster_no!=cslu2.cluster_no;"""

    citing_cited = pd.read_sql(citing_cited_query, con=engine)

    reduced_cluster_query = """
        SELECT count(DISTINCT aa.scp) as count_articles, count(DISTINCT auid) as count_authors
        FROM theta_plus.imm1985_1995_all_authors_full_graph aa
        JOIN theta_plus.imm1985_1995_article_score_unshuffled asu on asu.scp = aa.scp
        WHERE asu.article_score >= 1 AND aa.mcl_cluster_no=""" +str(cluster_num)+ """;"""

    reduced_cluster = pd.read_sql(reduced_cluster_query, con=engine)
    cluster_size = reduced_cluster.at[0, 'count_articles']
    num_authors = reduced_cluster.at[0, 'count_authors']

    external_degrees = external_cluster_degrees.set_index('cluster_no').at[cluster_num, 'ext_cluster_total_degrees']

    all_clusters = Counter(citing_cited['citing_cluster'].tolist() + citing_cited['cited_cluster'].tolist())
    del all_clusters[cluster_num] # delete the cluster for which values are being computed


    if (external_degrees > 0): 

        for k,v in all_clusters.items():
            if v > 1:

                author_union_query = """
                    SELECT DISTINCT aa.auid, aa.mcl_cluster_no, count(aa.scp) as count_articles
                    FROM theta_plus.imm1985_1995_all_authors_full_graph aa
                    JOIN theta_plus.imm1985_1995_article_score_unshuffled asu ON asu.scp = aa.scp
                    WHERE asu.article_score >= 1
                    GROUP BY aa.auid, aa.mcl_cluster_no
                    HAVING aa.mcl_cluster_no=""" + str(cluster_num) + """
                    UNION
                    SELECT DISTINCT aa.auid, aa.mcl_cluster_no, count(aa.scp) as count_articles
                    FROM theta_plus.imm1985_1995_all_authors_full_graph aa
                    JOIN theta_plus.imm1985_1995_article_score_unshuffled asu ON asu.scp = aa.scp
                    WHERE asu.article_score >= 1
                    GROUP BY aa.auid, aa.mcl_cluster_no
                    HAVING aa.mcl_cluster_no=""" + str(k) + """;"""

                author_union = pd.read_sql(author_union_query, con=engine)

                author_cluster = author_union[author_union['cluster_no']==cluster_num]
                author_connected_cluster = author_union[author_union['cluster_no']==k]

                author_total_intersection = len(author_cluster[['auid']].merge(author_connected_cluster[['auid']], how='inner'))
                author_total_union = len(author_cluster[['auid']].merge(author_connected_cluster[['auid']], how='outer'))

                author_cluster_non_single = author_cluster[author_cluster['count_articles']>1]
                author_connected_cluster_non_single = author_connected_cluster[author_connected_cluster['count_articles']>1]

                num_authors_non_single = len(author_cluster_non_single)
                connected_cluster_num_authors_non_single = len(author_connected_cluster_non_single)

                author_non_single_intersection = len(author_cluster_non_single[['auid']].merge(author_connected_cluster_non_single[['auid']], 
                                                                      how='inner'))
                author_non_single_union = len(author_cluster_non_single[['auid']].merge(author_connected_cluster_non_single[['auid']], 
                                                                      how='outer'))

                if author_total_union>0:
                    author_total_intersect_union_ratio = author_total_intersection/author_total_union
                else:
                    author_total_intersect_union_ratio = None

                if author_non_single_union>0:
                    author_non_single_intersect_union_ratio = author_non_single_intersection/author_non_single_union
                else:
                    author_non_single_intersect_union_ratio = None

                connected_reduced_cluster_query = """
                    SELECT count(DISTINCT aa.scp) as count_articles, count(DISTINCT aa.auid) as count_authors
                    FROM theta_plus.imm1985_1995_all_authors_full_graph aa
                    JOIN theta_plus.imm1985_1995_article_score_unshuffled asu on asu.scp = aa.scp
                    WHERE asu.article_score >= 1 AND aa.mcl_cluster_no=""" +str(k)+ """;"""

                connected_reduced_cluster = pd.read_sql(connected_reduced_cluster_query, con=engine)
                connected_cluster_size = connected_reduced_cluster.at[0, 'count_articles']
                connected_cluster_num_authors = connected_reduced_cluster.at[0, 'count_authors']

                result_dict = {'cluster_no':cluster_num,
                               'cluster_size': cluster_size,
                               'cluster_num_authors': num_authors,
                               'cluster_num_authors_non_single': num_authors_non_single,
                               'cluster_total_external_edges': external_degrees,
                               'connected_cluster_no':k, 
                               'connected_cluster_size': connected_cluster_size,
                               'connected_cluster_num_authors': connected_cluster_num_authors,
                               'connected_cluster_num_authors_non_single': connected_cluster_num_authors_non_single,
                               'count_common_edges':[v],
                               'common_author_prop': author_total_intersection / num_authors,
                               'author_total_intersection_count':author_total_intersection,
                               'author_total_union_count': author_total_union,
                               'author_total_intersect_union_ratio': author_total_intersect_union_ratio,
                               'author_non_single_intersection_count':author_non_single_intersection,
                               'author_non_single_union_count': author_non_single_union,
                               'author_non_single_intersect_union_ratio': author_non_single_intersect_union_ratio}

                pd.DataFrame.from_dict(result_dict).to_sql('superset_30_350_connected_clusters_edges_authors_article_scores', con=engine, schema=schema, if_exists='append', index=False)

    print("All Completed.")