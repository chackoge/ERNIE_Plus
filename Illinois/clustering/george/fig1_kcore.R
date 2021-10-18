# script to generate K-core data for figure 1. 
# George Chacko 10/18/2021
# Input is manually edited file from Eleanor Wedell's pdf
# https://unofficialwarnowlab.slack.com/archives/C02467U3JQ0/p1634574427226000

library(data.table); library(ggplot2)

# read input file
setwd('/Users/chackoge/repos/clustering_manuscripts/discovery')
x <- fread('k_core_cluster_sizes.csv')
# add node_coverage column 'nc' that expresses the size of K-core output
# as a percentage of total node count ()14,695,475)
x[,nc:=round(100*sum(V2)/(x[V1==1][,sum(V2)]),2),by="V1"]

# note that for k=1 and k=2 there are multiple components
# k=1 has 13 x[V1==1][,V2]
# k=2 has 2 x[V1==2][,V2]

pdf('fig1_kcore.pdf')
qplot(as.factor(V1),nc,data=x,size=V2) + theme_bw() + 
geom_jitter(width=0.02) + labs(x=("K"),y=("% node_coverage")) + theme(legend.position = "none")
dev.off()
