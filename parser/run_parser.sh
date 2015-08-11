#! /bin/bash

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 [INPUT: XML file or directory] [XML INPUT FORMAT: abstracts|pubmed|pmc|plos] [OUTNAME: name without file ending]"
  exit
fi

echo "Parsing XML docs"
java -ea -jar parser.jar $2 $1 $3.md.tsv $3.om.txt > $3.json
