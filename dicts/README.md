# `/dicts`: Dictionaries and Maps Directory

This directory contains dictionaries and maps that are useful for mention
extraction, entity linking, and feature extraction. It also contains some
utilities to create or update the dictionaries.

This document describes the contents, format, and origin of each file in this
directory.

## Dictionaries

* `hg19_genes.tsv`: a list of 17,801 human gene-symbols. 1 column: gene-symbol.
  Created from the loci file in the resource update with:

	```
	cut -f5 /cluster/u/amirma/Resource_Update_2013/GeneSet2013/human/excludeUnconventionals/hg19.loci | grep -V ENSG | sort -u > hg19_genes.tsv
	```

* `hugo_synonyms.tsv`: a gene-symbol synonyms table. Variable number of columns:
  1st column is the approved name, the other columns contain
  synonyms. Created using the get_hugo_synonyms.sh script (see below).

* `HGNC_approved_names.txt`: a table with more explicit nomeclature for gene
  symbols. It might be practical for literature mining of genes that are less
  studied. 3 columns: 1st column is gene symbol, 2nd column is CSV list of
  synonyms, 3rd column is explicit name/description of the gene (usually an
  expansion of the symbol). Downloaded from HGNC biomart.

* `hpo_terms.tsv`: a table listing HPO terms. 4 columns: 1st column is term ID,
  2nd column is term description, 3rd column is always C, 4th column is
  (probably) the distance from the root in the dag.

* `hpo_dag.tsv`: a table listing the "is a" relationships between HPO terms. 3
  columns: 1st column is first term ID, 2nd column is text "is a", 3rd column is
  second term ID. From the HPO.

* `genes_to_hpo_terms.tsv`: a table mapping gene-symbols to HPO terms. 3
  columns: 1st column is gene-symbol, 2nd column is HPO term id, 3rd column is
  description/name of the term. From the HPO.

* `genes_to_hpo_terms_with_synonyms.tsv`: an expanded table mapping gene-symbols
  and their synonyms to to HPO terms. 3 columns: 1st column is gene-symbol or
  synonym, 2nd column is HPO term id, 3rd column is description/name of the term. 

* `humanGeneSymbol.humanEnsembl.biomart73.map`: XXX What is this? 

* `english_words.tsv`: words in the English language

## Utilities

* `get_hugo_synonyms.sh`: Update the hugo_synonyms.tsv file by downloading and
  pre-processing the last version from Hugo.

