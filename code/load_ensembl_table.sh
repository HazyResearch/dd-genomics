#! /usr/bin/env bash

cat ${APP_HOME}/onto/data/ensembl_genes.tsv | awk '{OFS="\t"; print $1, $2}'
