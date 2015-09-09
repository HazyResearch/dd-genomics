#! /usr/bin/env bash

paste \
  <(cat ${APP_HOME}/onto/data/ensembl_genes.tsv | awk -F '[:\t]' '{OFS="\t"; print $1, $2}') \
  <(cat ${APP_HOME}/onto/data/ensembl_genes.tsv | awk -F '[\t]' '{OFS="\t"; print $2, $3}')

