#!/bin/bash

dir_name=$(dirname $1)

echo "dirname is $dir_name"

folder_name=$(echo $dir_name | cut -d '/' -f 3-10)

echo "folder name is $folder_name"

working_directory="/erniedev_data2/extended_uzzi/mcmc_calculations/"$folder_name

echo "working directory is $working_directory"

if [ ! -d "$working_directory/$2" ]; then
	mkdir -p $working_directory/$2 
	#mkdir $working_directory/$2
	#mkdir /erniedev_data10/P2_studies/background_file/working_directory/blast_$2/analysis
	#mkdir /erniedev_data10/P2_studies/background_file/working_directory/blast_$2/comparison
fi

echo "Getting name of input file to generate observed frequency file"

file_name=$(basename $1)

echo "input filename is $file_name"

file_name=$(echo $file_name | cut -d '.' -f 1)

echo "Filename $file_name"

#observed_frequency.py file calculates the frequency for all journal pairs in input dataset

/anaconda3/bin/python observed_frequency.py $1 $working_directory/${file_name}_observed_frequency.csv

if [ "$?" != 0 ]; then
	exit 1
fi

total=$(ls $dir_name/$2/*_permuted_* | wc -l)

echo "number of background files is $total"

#Using parallel command for background files frequency
ls $dir_name/$2/*_permuted_*.csv | parallel --halt soon,fail=1 --line-buffer --jobs 2 "set -e
/anaconda3/bin/python background_frequency.py {} $working_directory/$2/"


#For each simulation background file generateed by the permute method journal pairs frequency is calculated 
#for i in $(ls $dir_name/$2/*_permuted_*.csv)
#do
#	filename=$(basename $i)
#	number=$(echo $filename | tr -dc '0-9')
#	/anaconda3/bin/python background_frequency.py $filename $number $dir_name/$2/ $working_directory/$2/
#	if [ "$?" != 0 ]; then
#		exit 1
#	fi
#	#echo "Done file number $number"
#	echo " "
#done

#Mean, standard deviaiton and z_scores are calculated
/anaconda3/bin/python journal_count.py $working_directory/$2/ $total $working_directory/${file_name}_observed_frequency.csv
if [ "$?" != 0 ]; then
	exit 1
fi

#Generates file which contains all the journal_pairs, wos_id's, z_scores and observed frequency
/anaconda3/bin/python Table_generator.py $1 $working_directory/$2/zscores_file.csv $dir_name/${file_name}_permute.csv

if [ "$?" != 0 ]; then
	exit 1
fi

