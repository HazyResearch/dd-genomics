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
    section_id TEXT,
    ref_doc_id TEXT,
    sent_id TEXT,
    words TEXT[],
    lemmas TEXT[],
    poses TEXT[],
    ners TEXT[],
    dep_paths TEXT[],
    dep_parents INT[]
  )"
  if [ "${DBTYPE}" == "pg" ]; then
    SQL="${SQL_1};"
  else
    SQL="${SQL_1} DISTRIBUTED BY (doc_id, section_id);"
  fi
  psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -c "$SQL"
fi

echo "Copying to $TABLE table in database $DBNAME"
cat $INPUT | cut -f-4,6-9,11- | psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -X --set ON_ERROR_STOP=1 -c "COPY $TABLE FROM STDIN LOG ERRORS INTO sentences_err SEGMENT REJECT LIMIT 100000 ROWS"

echo "Done."
