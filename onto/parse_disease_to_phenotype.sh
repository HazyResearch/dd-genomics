#! /bin/bash

for i in `cat raw/omimDiseases.txt`
do
  grep -o 'HP:[0-9]*' raw/synopses/${i}.synopsis.txt | while read hpoid
  do
    echo -e "OMIM:${i}\t${hpoid}"
  done
done > manual/omim_disease_to_hpo.tsv
