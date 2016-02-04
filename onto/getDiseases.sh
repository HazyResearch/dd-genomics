#! /bin/zsh

#wget 'http://data.omim.org/downloads/Le_sy8F_SBKL0hYy6Bek9g/mimTitles.txt' -O raw/mimTitles.txt
catUncomment raw/mimTitles.txt | awk -F '\t' '{if ($1 == "Number Sign" || $1 == "Percent") print $2}' | sort | uniq > raw/omimDiseases.txt
mkdir -p raw/diseases
cat raw/omimDiseases.txt | while read id
do
  wget --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" \
    "http://api.omim.org/api/entry?mimNumber=${id}&include=alternativeNames&format=tsv&apiKey=1F2C6A581AC1E428183A107988EB56E579DE7F02" \
  -O raw/diseases/${id}.disease.txt
done
