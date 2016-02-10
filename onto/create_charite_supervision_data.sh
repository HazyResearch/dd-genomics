#! /bin/bash

cat manual/charite_all_sources_gene_to_pheno.tsv | cut -f 1,2 | sort | uniq > data/charite_supervision_ensgene.tsv
cat manual/charite_all_sources_gene_to_disease_to_pheno.tsv | awk '{OFS="\t"; print $3, $2}' | sort | uniq >> data/charite_supervision_ensgene.tsv
join -1 2 -2 2 -t $'\t' \
  <(cat manual/charite_all_sources_gene_to_disease_to_pheno.tsv | 
    cut -f 2,3 | sort | uniq | sort -k2,2) \
  <(cat manual/phenotypic_series_to_omim.tsv | 
    sort | uniq | sort -k2,2) |
  awk '{OFS="\t"; print $3, $2}' | sort | uniq >> data/charite_supervision_ensgene.tsv
join -1 2 -2 1 -t $'\t' \
  <(cat data/charite_supervision_ensgene.tsv | sort -k2,2) \
  <(cat data/ensembl_genes.tsv | 
    grep 'CANONICAL' | 
    awk -F '[:\t]' '{OFS="\t"; print $1, $2, $3, $4}' | 
    cut -f 1,3 | sort -k1,1) | 
    awk '{OFS="\t"; print $3, $2}' |
    sort | uniq > manual/charite_supervision.tsv
