#! /bin/zsh

git log --pretty=oneline genepheno_holdout_set.tsv | 
  cut -d ' ' -f 1 | 
  xargs -L 1 -I {} git show {}:onto/manual/genepheno_holdout_set.tsv | 
  grep '{' |
  sed 's/|~|/,/g' | 
  awk '{if (NF == 5) print $0}' | 
  sort | uniq | shuf > all_genepheno_holdout_sets.tsv
