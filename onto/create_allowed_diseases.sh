#! /bin/bash

cat manual/diseases.tsv manual/phenotypic_series.tsv | 
  ../code/create_allowed_diseases_list.py |
  cut -f 1 > manual/allowed_omim_ps.tsv
