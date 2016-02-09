#! /bin/bash

# Usually we'd use the "last stable build", but it appears to be messed up this time, so:
# wget 'http://compbio.charite.de/hudson/job/hpo.annotations.monthly/lastStableBuild/artifact/annotation/*zip*/annotation.zip'
wget http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/103/artifact/annotation/*zip*/annotation.zip
unzip annotation.zip
rm annotation.zip
mv annotation/ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt .
rm -r annotation
tail -n+2 ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt | sort -t $'\t' -k3,3 > entrez_disease_genes_to_phenotype.txt
rm ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt
join -t $'\t' -1 3 -2 2 entrez_disease_genes_to_phenotype.txt manual/gene.good_ensembl.entrez.map | 
  awk -F $'\t' '{OFS="\t"; print $4, $6, $2}' | 
  sort | uniq > manual/charite_all_sources_gene_to_disease_to_pheno.tsv
join -t $'\t' -1 3 -2 2 entrez_disease_genes_to_phenotype.txt manual/gene.good_ensembl.entrez.map | 
  awk -F $'\t' '{OFS="\t"; print $4, $6, $2}' | 
  sort | uniq |
  datamash -g 1,2 collapse 3 |
  awk '{OFS="\t"; print $1, $2, "{"$3"}"}'> manual/charite_all_sources_gene_to_pheno.tsv
rm entrez_disease_genes_to_phenotype.txt
