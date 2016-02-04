#! /bin/bash

for i in raw/diseases/*
do
  ./parse_diseases.py $i
done > manual/diseases.tsv
