#! /bin/bash

source ../env_local.sh

if [ "$#" != 2 ]; then
  echo "Usage: $0 [INPUT: input file] [table_name]"
  exit
fi

INPUT=$1
TABLE=$2

echo "Copying to $TABLE table in database $DBNAME"
echo "WARNING: After loading, pay attention if ref_doc_id and sent_id in sentences is flipped!"
echo "         This apparently happens sporadically. If it's the case, flip the dollar4 and dollar3 in the load_sentences script"
cat $INPUT | awk -F '\t' '{OFS="\t"; print $1, $2, $4, $3, $6, $7, $8, $9, $11, $12}' | psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -X --set ON_ERROR_STOP=1 -c "COPY $TABLE FROM STDIN LOG ERRORS INTO sentences_err SEGMENT REJECT LIMIT 100000 ROWS"

echo "Done."
