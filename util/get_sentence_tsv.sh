#!/bin/bash -e
set -beEu -o pipefail

if [ $# -ne 3 ]; then
  echo "$0: ERROR: wrong number of arguments"
  echo "$0: USAGE: $0 TABLE DOC_ID SENT_ID"
  exit 1
fi

TABLE=$1
DOC_ID=$2
SENT_ID=$3

SQL_CMD_FILE=/tmp/get_test_sent.sql
TSV_OUT_FILE=/tmp/test_sent_out.tsv

rm -rf ${SQL_CMD_FILE}
cat <<EOF >> ${SQL_CMD_FILE}
COPY (SELECT doc_id, sent_id, words, lemmas, poses, ners, dep_paths, dep_parents FROM $1 WHERE doc_id = '$2' AND sent_id = '$3' LIMIT 1) TO '${TSV_OUT_FILE}' WITH DELIMITER '\t';
EOF

psql -U ${DBUSER} -h ${DBHOST} -p ${DBPORT} ${DBNAME} -f ${SQL_CMD_FILE}

cp ${TSV_OUT_FILE} ${GDD_HOME}/test_sent_out.tsv
