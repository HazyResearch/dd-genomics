#! /bin/bash

source ../env_local.sh

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 [INPUT: input file] [table_name] [OP: new|add]"
  exit
fi

INPUT=$1
TABLE=$2
OP=$3

if [ ${OP} == "new" ]; then
  echo "Creating new table ${TABLE} in db"
  SQL_1="
  DROP TABLE IF EXISTS ${TABLE} CASCADE;
  CREATE TABLE ${TABLE} (
    doc_id TEXT,
    source_name TEXT,
    source_year INT,
    source_text_year TEXT,
    source_year_status TEXT,
    issn_global TEXT,
    issn_print TEXT,
    issn_electronic TEXT
  )"
  if [ "${DBTYPE}" == "pg" ]; then
    SQL="${SQL_1};"
  else
    SQL="${SQL_1} DISTRIBUTED BY (doc_id);"
  fi
  psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -c "$SQL"
fi

echo "Copying to $TABLE table in database $DBNAME"
cat $INPUT | ./md_cleanup.py | psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -X --set ON_ERROR_STOP=1 -c "COPY $TABLE FROM STDIN LOG ERRORS INTO md_err SEGMENT REJECT LIMIT 1000000 ROWS"

echo "Done."
