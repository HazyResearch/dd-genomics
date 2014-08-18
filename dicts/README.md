# /dicts: Dictionaries and Maps Directory

This directory contains dictionaries and maps that are useful for mention
extraction, entity linking, and feature extraction.

This document describes the contents, format, and origin of each file in this
directory.

## Dictionaries

* hg19_genes.tsv: a list of 17,801 human gene-symbols. 1 column: gene-symbol.
  Created from the loci file in the resource update with:

	cut -f5 /cluster/u/amirma/Resource_Update_2013/GeneSet2013/human/excludeUnconventionals/hg19.loci | grep -V ENSG | sort -u > hg19_genes.tsv

* hugo_synonyms.tsv: a gene-symbol synonyms table. Variable number of columns:
  1st column is the approved name, the other columns contain
  synonims. Created using the get_hugo_synonyms.sh script (see below).

* HGNC_approved_ames.txt: a table with more explicit nomeclature for gene
  symbols. It might be practical for literature mining of genes that are less
  studied. XXX What's the format of this file ? Downloaded from HGNC biomart.

* hpo_terms.tsv: a table listing HPO terms. 4 columns: 1st column is term ID,
  2nd column is term description, 3rd column is ? XXX, 4th column is ?
  XXX XXX Where does this file come from?

* hpo_dag.tsv: a table listing the "is a" relationships between HPO terms. 3
  columns: 1st column is first term ID, 2nd column is text "is a", 3rd column is
  second term ID. XXX Where does this file come from?

* genes_to_hpo_terms.tsv: a table mapping gene-symbols to HPO terms. 3 columns:
  1st column is gene-symbol, 2nd column is HPO term id, 3rd column is XXX . XXX
  Where does this file come from?

* genes_to_hpo_terms_with_synonyms.tsv: an expanded table mapping gene-symbols
  and their synonyms to to HPO terms. 3 columns: 1st column is gene-symbol or
  synonym, 2nd column is HPO term id, 3rd column is XXX . XXX Where does
  this file come from?. 

* humanGeneSymbol.humanEnsembl.biomart73.map: XXX What is this? 

## Utilities

* get_hugo_synonyms.sh: Update the hugo_synonyms.tsv file by downloading and
  pre-processing the last version from Hugo.

