#! /bin/zsh

wget --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" \
  'http://www.omim.org/phenotypicSeriesTitle/all?format=tab&apiKey=1F2C6A581AC1E428183A107988EB56E579DE7F02' \
  -O raw/phenotypic_series.tsv
cut -f 2 raw/phenotypic_series.tsv | awk '{if ($1 ~ "PS") print $0}' | while read i
mkdir -p raw/phenotypicSeries
do
  wget --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" \
    "http://www.omim.org/phenotypicSeries/${i}?sort=&order=&format=tab&apiKey=1F2C6A581AC1E428183A107988EB56E579DE7F02" \
    -O raw/phenotypicSeries/${i}.series.tsv
done
