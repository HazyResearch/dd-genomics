#! /bin/bash

source ../env_local.sh

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 [INPUT: XML DIR OR FILE] [OUT: DB TABLE] [new|add]"
  exit
fi

if [ "${BAZAAR_DIR-}" == "" ]; then
  echo "Please set BAZAAR_DIR in env_local.sh, as well as any other parameters."
  exit 1
fi
echo "Using bazaar installation at ${BAZAAR_DIR}"

echo "Parsing XML docs"
XML_OUT_NAME=xml_parsed.json
java -ea -jar parser.jar $1 > ${XML_OUT_NAME}

echo "Running NLP preprocessing"
$BAZAAR_DIR/parser/run_parallel.sh -in="${XML_OUT_NAME}" --parallelism=${PARALLELISM} -i json -k "item_id" -v "content"

if [ $3 == "create" ]; then
  echo "Creating new table in db"
  SQL_1="
  DROP TABLE IF EXISTS $2 CASCADE;
  CREATE TABLE $2 (
    doc_id TEXT,
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
    SQL="${SQL_1} DISTRIBUTED BY (doc_id);"
  fi
  psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -c "$SQL"
else
  echo "Adding to existing table $2 in db"
fi

echo "Copying to $2 table in database $DBNAME"
cat ${XML_OUT_NAME}.split/*.parsed | cut -f-2,4-7,9- | psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -c "COPY $2 FROM STDIN"

echo "To clean up, run: rm -rf ${XML_OUT_NAME}*"
