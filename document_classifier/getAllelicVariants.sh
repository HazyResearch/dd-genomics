#! /bin/zsh

i=1; while [[ $i -lt 20 ]]
do
  wget --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" \
    "http://www.omim.org/search?index=entry&exists=av_exists:true&sort=score+desc,+prefix_sort+desc&start=${i}&limit=200&format=tab" \
    -O allelicVariants${i}.tsv
  ((i = $i + 1))
done
