setwd('/srv/shared/external/for_eleanor/kc')
library(data.table); library(readr); library(ggplot2)

file_list <- list.files(pattern=glob2rx("*.csv"))
flist <- list()
for (i in 1:length(file_list)){
  flist[[i]] <- fread(file_list[i])
}
names(flist) <- paste(file_list)
flist2 <- list()

# V1 node_id
# V2 cluster_id
# V3 mcd
# V4 modularity

for (i in 1:length(flist)) {
flist2[[i]] <- flist[[i]][,.N,by=c('V2','V3','V4')][,condition:=names(flist[i])]
}

df_kc <- rbindlist(flist2)
fwrite(df_kc,file='df_kc.csv.txt')

# generate plot
k_vec <- readr::parse_number(df_kc$condition)
df_kc <- cbind(df_kc,k=k_vec)
temp <- df_kc[,max(N),by='k']

plot_df <- merge(temp, df_kc, by.x=c('k','V1'),by.y=c('k','N'))
plot_df[V4 >0, mod:='+ve']
plot_df[V4 <=0, mod:='-ve']

pdf('fig1_mod.pdf')
qplot(log10(k),log10(V1),data=plot_df,color=mod,xlab='log10(k)',ylab='log10(k-core size)') + theme_bw() + theme(text = element_text(size = 20))  
dev.off()
