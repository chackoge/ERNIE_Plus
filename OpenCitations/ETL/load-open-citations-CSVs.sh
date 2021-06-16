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

  absolute_file_dir=$(cd "${dir}" && pwd)
  absolute_file_path="${absolute_file_dir}/${name_with_ext}"

  # Stripping extra columns `journal_sc,author_sc` from `oci,citing,cited,creation,timespan,journal_sc,author_sc`
  # could be done via `COPY ... FROM PROGRAM 'cut -d "," -f 1-5 ':'file'''`, but it is probably not worth it.
  # language=PostgresPLSQL
  psql -v ON_ERROR_STOP=on --echo-all -v "file=${absolute_file_path}" << 'HEREDOC'
    COPY stg_open_citations(oci, citing, cited, creation, timespan, journal_sc, author_sc)
    FROM :'file' (FORMAT CSV, HEADER ON);
HEREDOC
done
