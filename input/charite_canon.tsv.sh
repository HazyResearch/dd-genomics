#! /usr/bin/env bash

cat ${APP_HOME}/input/charite.tsv | ${APP_HOME}/onto/canonicalize_gene_phenotype.sh
