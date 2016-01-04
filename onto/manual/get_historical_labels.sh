#! /bin/zsh

git log --pretty=oneline genepheno_holdout_labels.tsv | 
  cut -d ' ' -f 1 | 
  xargs -L 1 -I {} git show {}:onto/manual/genepheno_holdout_labels.tsv | 
  sed 's/|~|/,/g' | 
  awk '{if (NF == 6) print $0}' | 
  sort | uniq | shuf # > all_genepheno_holdout_labels.tsv
