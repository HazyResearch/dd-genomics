#! /bin/zsh

git log --pretty=oneline gene_holdout_set.tsv | 
  cut -d ' ' -f 1 | 
  xargs -L 1 -I {} git show {}:onto/manual/gene_holdout_set.tsv | 
  grep '{' |
  sed 's/|~|/,/g' | 
  awk '{if (NF == 5) print $0}' | 
  sort | uniq | shuf # > all_gene_holdout_sets.tsv
