#!/bin/bash
# Get mesh terms that map to phenotypes in HPO
cut -d $'\t' -f 7 data/hpo_phenotypes.tsv  | sort -u | tail -n +2 > data/meshList.txt
