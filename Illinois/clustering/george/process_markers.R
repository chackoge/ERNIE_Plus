setwd('/srv/local/shared/external/for_eleanor/gc_exosome')
# mapping markers from Kalluri & LeBleu (2020)to 
# IKC k10_b0 on Dimensions sabpq dataset

akr <- fread('annotated_kalluri_references.csv')
k10b0 <- fread('testing_k10_b0.csv')

# make header-free file intelligible
colnames(k10b0) <- c('integer_id','cluster_no','min_k','modularity')

# merge marker information with cluster data (inner join)
annotated_k10b0 <- merge(akr,k10b0,by.x='integer_id',by.y='integer_id')

# import cluster size data
k10b0_sizes <- fread('testing_k10_b0.csv.out')

# make cluster_size column names intelligible
colnames(k10b0_sizes) <- c('cluster_no','cluster_size')

# merge again 
k10b0_annotated_size <- merge(k10b0_sizes,annotated_k10b0,by.x='cluster_no',by.y='cluster_no')

# count markers in these clusters
