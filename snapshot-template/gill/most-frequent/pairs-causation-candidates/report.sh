#!/usr/bin/env bash

set -eu
inputName=data
outputName=data
EXPAND_PARAMETERS=true \
compile-xdocs "$inputName".sql.in
run-sql "$(cat "$inputName".sql)" CSV HEADER >"$outputName".csv
head -n 1 "$outputName".csv > "$outputName"2.csv
join -t $'\t' -1 2 -2 1 \
  <(tail -n+2 ${outputName}.csv | 
    sed 's/,/\t/g' | 
    sort -k2,2 | uniq) \
  <(cat ${APP_HOME}/onto/data/hpo_phenotypes.tsv | 
    cut -d '	' -f 1,2 | 
    tr ',' '/' |
    sort -k1,1 | uniq) | 
  awk -F '\t' '{print $1","$4","$2","$3}' | sort -t ',' -k4,4nr >> "$outputName"2.csv
json-for "$outputName"2.csv | transpose-json >"$outputName".json
