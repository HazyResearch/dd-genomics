#! /bin/bash

for i in raw/phenotypicSeries/PS*
do
  name=`tail -n+6 $i | head -n 1 | awk -F ' - ' '{print $1}' | ./replace_non_alpha.py`
  number=`tail -n+6 $i | head -n 1 | awk -F ' - ' '{print $2}'`
  echo -e "OMIM:${number}\t${name}"
done > manual/phenotypic_series.tsv

for i in raw/phenotypicSeries/PS*
do
  number=`tail -n+6 $i | head -n 1 | awk -F ' - ' '{print $2}' | ./replace_non_alpha.py`
  for omimNumber in `tail -n+8 $i | awk -F '\'t '{if (length($0) == 0) {exit}; print $4}'`
  do
    echo -e "OMIM:${number}\tOMIM:${omimNumber}"
  done
done > manual/phenotypic_series_to_omim.tsv
