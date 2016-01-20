#! /bin/zsh

join -1 1 -2 1 \
  <(git log --pretty=oneline genepheno_holdout_set.tsv | 
    cut -d ' ' -f 1 |
    xargs -L 1 -I {} git show {}:onto/manual/genepheno_holdout_set.tsv |
    grep '{' |
    sed 's/|~|/,/g' |
    awk '{if (NF == 5) print $0}' |
    sort | uniq | cut -f 1-3 | sort | uniq -c | awk '{if ($1 == 1) print $2":"$3":"$4}' |
    sort) \
  <(git log --pretty=oneline genepheno_holdout_set.tsv | 
    cut -d ' ' -f 1 | 
    xargs -L 1 -I {} git show {}:onto/manual/genepheno_holdout_set.tsv | 
    grep '{' |
    sed 's/|~|/,/g' | 
    awk '{if (NF == 5) print $0}' | 
    sort | uniq | awk '{print $1":"$2":"$3"\t"$4"\t"$5}' | sort -k1,1) |
  sed 's/:/\t/g' | shuf
