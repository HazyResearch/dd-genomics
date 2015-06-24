#! /bin/bash

if [ "$#" -l 1 ]; then
  echo "Usage: $0 input_xml_dir_or_file"
  exit
fi

BAZAAR_DIR=`cd ../../bazaar/parser; pwd`
echo "Using bazaar installation at ${BAZAAR_DIR}"

echo "Parsing XML docs"
XML_OUT_NAME=xml_parsed.json
java -ea -jar parser.jar $1 > ${XML_OUT_NAME}

echo "Running NLP preprocessing"
$BAZAAR_DIR/run_parallel.sh -in="${XML_OUT_NAME}" --parallelism=50 -i json -k "item_id" -v "content"
