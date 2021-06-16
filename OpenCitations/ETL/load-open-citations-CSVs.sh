#!/usr/bin/env bash
for file in *.csv; do
  echo "Processing ${file} ..."

  if [[ "${file}" != */* ]]; then
    file=./${file}
  fi
  # Remove shortest /* suffix
  dir=${file%/*}
  # dir = '.' for files in the current directory

  # Remove longest */ prefix
  name_with_ext=${file##*/}

  absolute_file_dir="$(cd ${dir} && pwd)"
  absolute_file_path="${absolute_file_dir}/${name_with_ext}"

  #FIXME Strip extra columns via `pcregrep` piping to the stdin
  # language=PostgresPLSQL
  psql -v ON_ERROR_STOP=on --echo-all -v "file=${absolute_file_path}" << 'HEREDOC'
    COPY open_citations (oci, citing, cited, creation_date, time_span) FROM :'file' (FORMAT CSV, HEADER ON);
HEREDOC
done
