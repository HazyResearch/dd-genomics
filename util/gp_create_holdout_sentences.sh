#!/bin/bash -e
set -beEu -o pipefail

if [ $# -ne 1 ]; then
	echo "$0: ERROR: wrong number of arguments" >&2
	echo "$0: USAGE: $0 DB" >&2
	exit 1
fi

DB=$1

TMPDIR=$(mktemp -d /tmp/dft.XXXXXX)
SQL_COMMAND_FILE=${TMPDIR}/dft.sql
cat <<EOF >> ${SQL_COMMAND_FILE}
DELETE FROM genepheno_holdout_set 
WHERE (doc_id, section_id, sent_id, gene_wordidxs, pheno_wordidxs) IN 
(SELECT DISTINCT
  s.* 
FROM
  genepheno_holdout_set s 
  LEFT JOIN 
  genepheno_pairs p 
    ON (s.doc_id = p.doc_id AND s.section_id = p.section_id AND s.sent_id = p.sent_id AND s.gene_wordidxs = STRING_TO_ARRAY(p.gene_wordidxs, '|~|')::INTEGER[] AND s.pheno_wordidxs = STRING_TO_ARRAY(p.pheno_wordidxs, '|~|')::INTEGER[]) WHERE p.doc_id IS NULL);

DELETE FROM genepheno_holdout_labels 
WHERE (doc_id, section_id, sent_id) NOT IN 
(SELECT DISTINCT doc_id, section_id, sent_id FROM genepheno_holdout_set);

DROP TABLE IF EXISTS sentences_input_with_holdout_gp;
CREATE TABLE sentences_input_with_holdout_gp AS (
  SELECT si.*
  FROM 
    sentences_input_with_gene_mention si
    JOIN genepheno_holdout_set s
      ON (si.doc_id = s.doc_id)
) DISTRIBUTED BY (doc_id);
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} > /dev/stderr
rm -rf ${TMPDIR}

