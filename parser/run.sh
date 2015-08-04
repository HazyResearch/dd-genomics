#! /bin/bash

source ../env_local.sh

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 [INPUT: XML file or directory] [OUT: DB table name] [OPERATION: new|add] [XML FORMAT: abstracts|pubmed|pmc|plos]"
  exit
fi

if [ "${BAZAAR_DIR-}" == "" ]; then
  echo "Please set BAZAAR_DIR in env_local.sh, as well as any other parameters."
  exit 1
fi
echo "Using bazaar installation at ${BAZAAR_DIR}"

echo "Parsing XML docs"
XML_OUT=xml_parsed
java -ea -jar parser.jar $4 $1 ${XML_OUT}.md.tsv ${XML_OUT}.om.txt > ${XML_OUT}.json

echo "Running NLP preprocessing"
$BAZAAR_DIR/parser/run_parallel.sh -in="${XML_OUT}.json" --parallelism=40 -i json -k "doc-id,section-id,ref-doc-id" -v "content"

if [ $3 == "create" ]; then
  echo "Creating new table in db"
  SQL_1="
  DROP TABLE IF EXISTS $2 CASCADE;
  CREATE TABLE $2 (
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
else
  echo "Adding to existing table $2 in db"
fi

echo "TODO: Load metadata into db"

echo "Copying to $2 table in database $DBNAME"
cat ${XML_OUT_NAME}.split/*.parsed | cut -f-4,6-9,11- | psql -U $DBUSER -h $DBHOST -p $DBPORT $DBNAME -c "COPY $2 FROM STDIN"

echo "To clean up, run: rm -rf ${XML_OUT}*"
