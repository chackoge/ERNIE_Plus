# Systematic approach to compare clusterings
# George Chacko 10/9/2021

library(data.table)

#vanilla Leiden clustering is in /srv/local/shared/external/minhyuk2/exosome_1900_2010_sabpq/leiden
# read in vanilla Leiden r=0.05
vl_05 <- fread('/srv/local/shared/external/minhyuk2/exosome_1900_2010_sabpq/leiden/leiden_0.05.cluster_to_id.clusters')
## Note that V1 is cluster no and V2 is node_id
vl_05_counts <- vl_05[,.N,by='V1']
# change colname for vl_05 because of inconsistent column order
colnames(vl_05_counts)[1] <- 'V2'

# base IKC data is in /srv/local/shared/external/for_eleanor/gc_exosome
# read in ikc5 data
ikc5 <- fread('/srv/local/shared/external/for_eleanor/gc_exosome/testing_k5_b0.csv')
ikc5_counts <- ikc5[,.N,by='V2']

# Leiden kmp is in /srv/shared/external/for_eleanor/leiden/core_analysis
# read in Leiden kmp processed r=0.05,k5,p2 data
lkmp_r05_k5_p2 <- fread('/srv/shared/external/for_eleanor/leiden/core_analysis/leiden_KCp_0.05_k_5_p_2.analysis') 
lkmp_r05_k5_p2_counts <- lkmp_r05_k5_p2[,.N,by='V2'][order(-N)]

# the IKC+augmentation kmp parsed results are in /srv/shared/external/for_eleanor/ikc+augmentation
# read in ikc+aug kmp processed at k=5
ikc5_aug_kmp <- fread('/srv/shared/external/for_eleanor/ikc+augmentation/ikcaug_k_5_p_2.coreanalysis')
ikc5_aug_kmp_counts <- ikc5_aug_kmp[,.N,by='V2']

# the IKC+RG+AUG kmp parsed results are in /srv/shared/external/for_eleanor/ikc+rg+aug
# read in ikc_rg_aug kmp processed at k=5
ikc5_rg_aug_kmp <- fread('/srv/shared/external/for_eleanor/ikc+rg+aug/ikc-rg-aug_k_5_p_2.clustering')
ikc5_rg_aug_kmp_counts <- ikc5_rg_aug_kmp[,.N,by='V2']

total_nodes <- dim(ikc5)[1]

# Process vLeiden_05
print("***vLeiden 05***")
print(paste("Num non-singleton clusters",dim(vl_05_counts[N>1])[1]))
print(paste("vLeiden Node Coverage:", round(100*vl_05_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("vl05 cluster size distribution:")
vLeiden_05 <- vl_05_counts[N>1][,summary(N)]
print(vLeiden_05)
vLeiden_05 <- c(unname(vLeiden_05),dim(vl_05_counts[N>1])[1],round(100*vl_05_counts[N>1][,sum(N)]/total_nodes,2))


# Process ikc5
print("***ikc5***")
print(paste("Num non-singleton clusters",dim(ikc5_counts[N>1])[1]))
print(paste0("ikc5 Node Coverage:", round(100*ikc5_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("ikc5 cluster size distribution:")
vikc5 <- ikc5_counts[N>1][,summary(N)]
print(vikc5)
vikc5 <- c(unname(vikc5),dim(ikc5_counts[N>1])[1],round(100*ikc5_counts[N>1][,sum(N)]/total_nodes,2))

# Process Leiden kmp data lkmp_r05_k5_p2_counts
print("***Leiden r=0.05 kmp processed k=5 p=2***")
print(paste("Num non-singleton clusters",dim(ikc5_counts[N>1])[1]))
print(paste("Leiden kmp k=5 p-2 Node Coverage:", round(100*lkmp_r05_k5_p2_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("Leiden kmp k=5 p=2 cluster size distribution:")
vkmpLeiden_05 <- lkmp_r05_k5_p2_counts[N>1][,summary(N)]
print(vkmpLeiden_05)
vkmpLeiden_05  <- c(unname(vkmpLeiden_05),dim(lkmp_r05_k5_p2_counts[N>1])[1],round(100*lkmp_r05_k5_p2_counts[N>1][,sum(N)]/total_nodes,2))


# Process IKC + Aug data k=5 
print("***ikc5 + Aug p=2***")
print(paste("Num non-singleton clusters",dim(ikc5_aug_kmp_counts[N>1])[1]))
print(paste("IKC + Aug k=5 p=2 Node Coverage:", round(100*ikc5_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("Leiden kmp k=5 p=2 cluster size distribution:")
vikc5_aug <- ikc5_aug_kmp_counts [N>1][,summary(N)]
print(vikc5_aug)
vikc5_aug <- c(unname(vikc5_aug),dim(ikc5_aug_kmp_counts[N>1])[1],round(100*ikc5_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2))

# Process IKC + RG + Aug data k = 5
print("***ikc5 + RG + Aug p=2***")
print(paste("Num non-singleton clusters",dim(ikc5_rg_aug_kmp_counts[N>1])[1]))
print(paste("IKC + RG + Aug k=5 p=2 Node Coverage:", round(100*ikc5_rg_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2),'%'))
print("Leiden kmp k=5 p=2 cluster size distribution:")
vikc5_rg_aug <- ikc5_rg_aug_kmp_counts[N>1][,summary(N)]
print(vikc5_rg_aug)
vikc5_rg_aug <- c(unname(vikc5_rg_aug),dim(ikc5_rg_aug_kmp_counts[N>1])[1],round(100*ikc5_rg_aug_kmp_counts[N>1][,sum(N)]/total_nodes,2))

df <- data.frame(rbind(vLeiden_05,vikc5,vkmpLeiden_05,vikc5_aug,vikc5_rg_aug))
colnames(df) <- c('min','Q1','median','mean','Q3','max','cluster_count','node_coverage_perc')
print(df)

markers <- fread('/srv/local/shared/external/for_eleanor/gc_exosome/marker_nodes_integer_pub.csv')

# tag each counts df before rbinding them

vl_05_counts[,clustering:='vleiden_5']
ikc5_counts[,clustering:='ikc5']
lkmp_r05_k5_p2_counts[,clustering:='leiden_kmp_5_2']
ikc5_aug_kmp_counts[,clustering:='ikc5_aug']
ikc5_rg_aug_kmp_counts[,clustering:='ikc5_rg_aug']

all <- rbind(vl_05_counts,ikc5_counts,lkmp_r05_k5_p2_counts,ikc5_aug_kmp_counts,ikc5_rg_aug_kmp_counts)
pdf('ikc5_boxplots.pdf')
qplot(as.factor(clustering),log10(N),data=all[N>1],geom='boxplot',xlab='clustering',ylab='log10 cluster size')  + theme_bw()
dev.off()