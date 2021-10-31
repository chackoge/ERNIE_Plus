# generate an IKC scatter plot
rm(list=ls()); library(data.table); library(ggplot2)
setwd('/srv/local/shared/external/clusterings/exosome_1900_2010_sabpq/ikc')

ikc5 <- fread('testing_k5_b0.csv')
ikc10 <- fread('testing_k10_b0.csv')
ikc20 <- fread('testing_k20_b0.csv')
ikc30 <- fread('testing_k30_b0.csv')
ikc40 <- fread('testing_k40_b0.csv')
ikc50 <- fread('testing_k50_b0.csv')

# no time to be other than clunky
ikc5_counts <-  ikc5[,.N,by=c('V2','V3')][N > 1][,.(cno=V2,mcd=V3,csize=N)]
ikc5_counts[,label:='ikc5']

ikc10_counts <-  ikc10[,.N,by=c('V2','V3')][N > 1][,.(cno=V2,mcd=V3,csize=N)]
ikc10_counts[,label:='ikc10']

ikc20_counts <-  ikc20[,.N,by=c('V2','V3')][N > 1][,.(cno=V2,mcd=V3,csize=N)]
ikc20_counts[,label:='ikc20']

ikc30_counts <-  ikc30[,.N,by=c('V2','V3')][N > 1][,.(cno=V2,mcd=V3,csize=N)]
ikc30_counts[,label:='ikc30']

ikc40_counts <-  ikc40[,.N,by=c('V2','V3')][N > 1][,.(cno=V2,mcd=V3,csize=N)]
ikc40_counts[,label:='ikc40']

ikc50_counts <-  ikc50[,.N,by=c('V2','V3')][N > 1][,.(cno=V2,mcd=V3,csize=N)]
ikc50_counts[,label:='ikc50']

ikc_all <- rbind(ikc5_counts, ikc10_counts, ikc20_counts, ikc30_counts, ikc40_counts, ikc50_counts)
setwd('/srv/local/shared/external/verified_clusterings/figures')

# save data
fwrite(ikc_all,file='fig2_data.csv')

# generate plot

x <- fread('fig2_data.csv')
x$label <- factor(x$label, levels=c('ikc5','ikc10', 'ikc20', 'ikc30', 'ikc40', 'ikc50'))
pdf('fig2.pdf')
qplot(mcd,log10(csize),data=x,facets=label~.,color=label, ylab='log10(cluster_size)') + theme_bw() +
theme(legend.position='none') + theme(text = element_text(size = 18)) 
dev.off()






