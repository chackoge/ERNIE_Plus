import pandas as pd
from sqlalchemy import create_engine
from sys import argv

user_name = argv[1]
password = argv[2]
data_type = argv[3] # 'imm' or 'eco'
start_year = argv[4]
end_year = argv[5]
start_val = int(argv[6])
match_type = argv[7] # 'overlap' or 'jaccard'
schema = argv[8]
sql_scheme= 'postgresql://' + user_name + ':' + password + '@localhost:5432/ernie'
engine = create_engine(sql_scheme)

table_name = data_type + start_year + '_' + end_year

main_table_query = """
SELECT s.""" + table_name + """_cluster_number, s.""" + table_name + """_cluster_size,
       s.""" + match_type + """_match_year AS mcl_match_year, s.""" + match_type + """_match_cluster_no 
       AS mcl_year_cluster_no, s.""" + match_type + """_match_proportion 
       AS superset_year_""" + match_type + """_match_prop
FROM theta_plus.superset_to_year_match_30_350 s
ORDER BY s.""" + table_name + """_cluster_number ASC
"""

main_table = pd.read_sql(main_table_query, con=engine)
main_table.name = 'superset_30_350_mcl_graclus_all_data' + match_type 

main_table['mcl_match_year'] = main_table['mcl_match_year'].str[3:7]

new_columns = ['mcl_year_cluster_size', 'mcl_year_conductance','mcl_year_coherence', 'mcl_year_int_edges', 
               'mcl_year_boundary', 'mcl_year_sum_article_score', 'mcl_year_max_article_score',
               'mcl_year_median_article_score', 'graclus_half_mclsize_cluster_no','graclus_half_mclsize_cluster_size', 
               'graclus_half_mclsize_to_mcl_ratio','graclus_half_mclsize_total_intersection',
               'graclus_half_mclsize_total_union', 'graclus_half_mclsize_intersection_union_ratio',
               'graclus_half_mclsize_multiple_options', 'graclus_half_mclsize_conductance',
               'graclus_half_mclsize_coherence','graclus_half_mclsize_int_edges', 'graclus_half_mclsize_boundary', 
               'graclus_half_mclsize_sum_article_score','graclus_half_mclsize_max_article_score',
               'graclus_half_mclsize_median_article_score']

for column in new_columns:
    main_table[column] = None
    
print(f'Working on table: {schema}.{main_table.name}')
print(f'The size of the table is {len(main_table)}')

save_name = main_table.name

for i in range(start_val, len(main_table)):
    
    match_year = 'imm' + str(main_table.at[i, 'mcl_match_year'])
    mcl_year_table_name = match_year + "_all_merged_unshuffled"
    mcl_year_cluster_no = str(main_table.at[ i, 'mcl_year_cluster_no'])
    mcl_year_query = "SELECT cluster_size, conductance, coherence, int_edges, boundary, sum_article_score, max_article_score, median_article_score FROM theta_plus." + mcl_year_table_name + " WHERE cluster_no=" + mcl_year_cluster_no + ";"
    
    graclus_half_mclsize_cluster_no_query = "SELECT * FROM theta_plus." + match_year + "_match_to_graclus_half_mclsize WHERE mcl_cluster_no=" + mcl_year_cluster_no + ";"
    graclus_half_mclsize_cluster_no_table = pd.read_sql(graclus_half_mclsize_cluster_no_query, con=engine)
    graclus_half_mclsize_cluster_no = graclus_half_mclsize_cluster_no_table.at[0, 'graclus_cluster_no']
    graclus_half_mclsize_table_name = match_year + "_all_merged_graclus_half_mclsize"
    graclus_half_mclsize_query = "SELECT coherence, conductance, int_edges, boundary, sum_article_score, max_article_score, median_article_score FROM theta_plus." + graclus_half_mclsize_table_name + " WHERE cluster_no=" + str(graclus_half_mclsize_cluster_no) + ";"
    
    mcl_year_table = pd.read_sql(mcl_year_query, con=engine)
    graclus_half_mclsize_table = pd.read_sql(graclus_half_mclsize_query, con=engine)
    
    main_table.at[i, 'mcl_year_cluster_size'] = mcl_year_table.at[0, 'cluster_size']
    main_table.at[i, 'mcl_year_conductance'] = mcl_year_table.at[0, 'conductance']
    main_table.at[i,'mcl_year_coherence'] = mcl_year_table.at[0, 'coherence']
    main_table.at[i,'mcl_year_int_edges'] =  mcl_year_table.at[0, 'int_edges']
    main_table.at[i,'mcl_year_boundary'] = mcl_year_table.at[0, 'boundary']
    main_table.at[i,'mcl_year_sum_article_score'] = mcl_year_table.at[0, 'sum_article_score']
    main_table.at[i,'mcl_year_max_article_score'] = mcl_year_table.at[0, 'max_article_score']
    main_table.at[i,'mcl_year_median_article_score'] = mcl_year_table.at[0, 'median_article_score']
    
    main_table.at[i,'graclus_half_mclsize_cluster_no'] = graclus_half_mclsize_cluster_no
    main_table.at[i,'graclus_half_mclsize_cluster_size'] = graclus_half_mclsize_cluster_no_table.at[0, 'graclus_cluster_size']
    main_table.at[i,'graclus_half_mclsize_to_mcl_ratio'] = graclus_half_mclsize_cluster_no_table.at[0, 'graclus_to_mcl_ratio']
    main_table.at[i,'graclus_half_mclsize_total_intersection'] = graclus_half_mclsize_cluster_no_table.at[0, 'total_intersection']
    main_table.at[i,'graclus_half_mclsize_total_union'] = graclus_half_mclsize_cluster_no_table.at[0, 'total_union']
    main_table.at[i,'graclus_half_mclsize_intersection_union_ratio'] = graclus_half_mclsize_cluster_no_table.at[0, 'intersect_union_ratio']
    main_table.at[i,'graclus_half_mclsize_multiple_options'] = graclus_half_mclsize_cluster_no_table.at[0, 'multiple_options']
    
    main_table.at[i,'graclus_half_mclsize_conductance'] = graclus_half_mclsize_table.at[0, 'conductance']
    main_table.at[i,'graclus_half_mclsize_coherence'] = graclus_half_mclsize_table.at[0, 'coherence']
    main_table.at[i,'graclus_half_mclsize_int_edges'] = graclus_half_mclsize_table.at[0, 'int_edges']
    main_table.at[i,'graclus_half_mclsize_boundary'] = graclus_half_mclsize_table.at[0, 'boundary']
    main_table.at[i,'graclus_half_mclsize_sum_article_score'] = graclus_half_mclsize_table.at[0, 'sum_article_score']
    main_table.at[i,'graclus_half_mclsize_max_article_score'] = graclus_half_mclsize_table.at[0, 'max_article_score']
    main_table.at[i,'graclus_half_mclsize_median_article_score'] = graclus_half_mclsize_table.at[0, 'median_article_score']

    result_df = main_table[i:i+1]
    result_df = result_df.astype(float)
    result_df.to_sql(save_name, schema=schema, con=engine, if_exists='append', index=False)

print("Done updating table.")
print("All completed.")