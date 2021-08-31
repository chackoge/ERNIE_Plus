library(data.table)
fl <- list.files(pattern='test.*..csv')
output <- list()
for (i in 1:length(fl)){
  output[[i]] <- fread(fl[i])
}

for (i in 1:length(output)){
print(fl[i])
t <- (output[[i]])[,.N,by='V2'][N>1][order(-N)]
print(paste("The number of clusters is", dim(t)[1]))
print(summary(t$N))
print('***')
print('')
fwrite(t,file=paste0(fl[i],'.out'))
}
