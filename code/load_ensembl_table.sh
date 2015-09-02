#! /usr/bin/env bash

cat ${APP_HOME}/onto/data/ensembl_genes.tsv | awk -F '[:\t]' '{OFS="\t"; print $1":"$2":"$3, $1, $2, $3, $4}'
