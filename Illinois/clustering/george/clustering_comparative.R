# Systematic approach to compare clusterings
# George Chacko 10/9/2021
# The purpose of this script is to compare clusterings by overlaying a set of 
# 1218 marker nodes on the clusters to identify clusters of interest
# In other words, clusters in which markers are concentrated.

library(data.table)

## read in cluster data
#vanilla Leiden clustering is in /srv/local/shared/external/minhyuk2/exosome_1900_2010_sabpq/leiden
# read in vanilla Leiden r=0.05
vl_05 <- fread('/srv/local/shared/external/minhyuk2/exosome_1900_2010_sabpq/leiden/leiden_0.05.cluster_to_id.clusters')

# base IKC data is in /srv/local/shared/external/for_eleanor/gc_exosome
# read in ikc5 data
ikc5 <- fread('/srv/local/shared/external/for_eleanor/gc_exosome/testing_k5_b0.csv')

# Leiden kmp is in /srv/shared/external/for_eleanor/leiden/core_analysis
# read in Leiden kmp processed r=0.05,k5,p2 data
lkmp_r05_k5_p2 <- fread('/srv/shared/external/for_eleanor/leiden/core_analysis/leiden_KCp_0.05_k_5_p_2.analysis') 

# the IKC+augmentation kmp parsed results are in /srv/shared/external/for_eleanor/ikc+augmentation
# read in ikc+aug kmp processed at k=5
ikc5_aug_kmp <- fread('/srv/shared/external/for_eleanor/ikc+augmentation/ikcaug_k_5_p_2.coreanalysis')

# the IKC+RG+AUG kmp parsed results are in /srv/shared/external/for_eleanor/ikc+rg+aug
# read in ikc_rg_aug kmp processed at k=5
ikc5_rg_aug_kmp <- fread('/srv/shared/external/for_eleanor/ikc+rg+aug/ikc-rg-aug_k_5_p_2.clustering')

## Generate cluster size data

# Note that V1 is cluster no and V2 is node_id for this clustering
vl_05_counts <- vl_05[,.N,by='V1']
# change colname for vl_05 because of inconsistent column order
colnames(vl_05_counts)[1] <- 'V2'

#ikc5 cluster sizes
ikc5_counts <- ikc5[,.N,by='V2']

# kmp processed leiden cluster sizes
kmp_leiden_r05_k5_p2_counts <- lkmp_r05_k5_p2[,.N,by='V2'][order(-N)]

# ikc5_aug_kmp processed cluster sizes
ikc5_aug_kmp_counts <- ikc5_aug_kmp[,.N,by='V2']

# ikc5_rg_aug kmp processed cluster sizes
ikc5_rg_aug_kmp_counts <- ikc5_rg_aug_kmp[,.N,by='V2']

# total node count for input data to all clusterings (exosome sabpq data set has 14 million nodes plus)
total_nodes <- dim(ikc5)[1]

# Process vLeiden_05 (vanilla Leiden at resolution factor 0.05 and CPM)

print("***vLeiden 05***")
print(paste("Num non-singleton clusters",dim(vl_05_counts[N>1])[1]))
print(paste("vLeiden Node Coverage:", round(100*vl_05_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("vl05 cluster size summary:")
# generate vector of statistics v is for vector
vvLeiden_05 <- vl_05_counts[N>1][,summary(N)]
print(vLeiden_05)
vvLeiden_05 <- c(unname(vvLeiden_05),dim(vl_05_counts[N>1])[1],round(100*vl_05_counts[N>1][,sum(N)]/total_nodes,2))


# Process ikc5
print("***ikc5***")
print(paste("Num non-singleton clusters",dim(ikc5_counts[N>1])[1]))
print(paste0("ikc5 Node Coverage:", round(100*ikc5_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("ikc5 cluster size distribution:")
vikc5 <- ikc5_counts[N>1][,summary(N)]
print(vikc5)
vikc5 <- c(unname(vikc5),dim(ikc5_counts[N>1])[1],round(100*ikc5_counts[N>1][,sum(N)]/total_nodes,2))

# Process Leiden kmp data kmp_leiden_r05_k5_p2_counts
print("***Leiden r=0.05 kmp processed k=5 p=2***")
print(paste("Num non-singleton clusters",dim(kmp_leiden_r05_k5_p2_counts[N>1])[1]))
print(paste("Leiden kmp k=5 p-2 Node Coverage:", round(100*kmp_leiden_r05_k5_p2_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("Leiden kmp k=5 p=2 cluster size distribution:")
vkmpLeiden_05 <- kmp_leiden_r05_k5_p2_counts[N>1][,summary(N)]
print(vkmpLeiden_05)
vkmpLeiden_05  <- c(unname(vkmpLeiden_05),dim(kmp_leiden_r05_k5_p2_counts[N>1])[1],round(100*kmp_leiden_r05_k5_p2_counts[N>1][,sum(N)]/total_nodes,2))


# Process IKC + Aug data k=5 
print("***ikc5 + Aug p=2***")
print(paste("Num non-singleton clusters",dim(ikc5_aug_kmp_counts[N>1])[1]))
print(paste("IKC + Aug k=5 p=2 Node Coverage:", round(100*ikc5_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("kmp processed IKC + Aug k=5 p=2 cluster size distribution:")
vikc5_aug <- ikc5_aug_kmp_counts [N>1][,summary(N)]
print(vikc5_aug)
vikc5_aug <- c(unname(vikc5_aug),dim(ikc5_aug_kmp_counts[N>1])[1],round(100*ikc5_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2))

# Process IKC + RG + Aug data k = 5
print("***ikc5 + RG + Aug p=2***")
print(paste("Num non-singleton clusters",dim(ikc5_rg_aug_kmp_counts[N>1])[1]))
print(paste("IKC + RG + Aug k=5 p=2 Node Coverage:", round(100*ikc5_rg_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("kmp processed IKC+RG+Aug k=5 p=2 cluster size distribution:")
vikc5_rg_aug <- ikc5_rg_aug_kmp_counts[N>1][,summary(N)]
print(vikc5_rg_aug)
vikc5_rg_aug <- c(unname(vikc5_rg_aug),dim(ikc5_rg_aug_kmp_counts[N>1])[1],round(100*ikc5_rg_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2))

df <- data.frame(rbind(vvLeiden_05,vikc5,vkmpLeiden_05,vikc5_aug,vikc5_rg_aug))
colnames(df) <- c('min','Q1','median','mean','Q3','max','cluster_count','node_coverage_perc')
print(df)

markers <- fread('/srv/local/shared/external/for_eleanor/gc_exosome/marker_nodes_integer_pub.csv')

# tag each counts df before rbinding them

vl_05_counts[,clustering:='vleiden_5']
ikc5_counts[,clustering:='ikc5']
kmp_leidenl_r05_k5_p2_counts[,clustering:='leiden_kmp_5_2']
ikc5_aug_kmp_counts[,clustering:='ikc5_aug']
ikc5_rg_aug_kmp_counts[,clustering:='ikc5_rg_aug']

all <- rbind(vl_05_counts,ikc5_counts,lkmp_r05_k5_p2_counts,ikc5_aug_kmp_counts,ikc5_rg_aug_kmp_counts)
pdf('ikc5_boxplots.pdf')
qplot(as.factor(clustering),log10(N),data=all[N>1],geom='boxplot',xlab='clustering',ylab='log10 cluster size')  + theme_bw()
dev.off()