#! /bin/bash

source ../env_local.sh

if [ "$#" != 2 ]; then
  echo "Usage: $0 [INPUT: input file] [table_name]"
  exit
fi

INPUT=$1
TABLE=$2

echo "Copying to $TABLE table in database $DBNAME"
cat $INPUT | cut -f1,2,4,3,6-9,11- | psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -X --set ON_ERROR_STOP=1 -c "COPY $TABLE FROM STDIN LOG ERRORS INTO sentences_err SEGMENT REJECT LIMIT 100000 ROWS"

echo "Done."
