#! /usr/bin/env bash

${APP_HOME}/onto/canonicalize_gene_phenotype.py ${APP_HOME}/input/charite.tsv | sort | uniq
