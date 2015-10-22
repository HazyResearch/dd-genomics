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
SELECT
  fp.labeler LABELER_CAUSATION,
  tp.tp true_pos,
  fp.fp false_pos,
  (tp.tp + fp.fp) positives,
  (tp.tp::float / (tp.tp::float + fp.fp::float)) as precision
FROM
  (SELECT
    labeler,
    COUNT(DISTINCT relation_id) fp
  FROM
    genepheno_causation_is_correct_inference gc 
    JOIN genepheno_holdout_set s 
      ON (s.doc_id = gc.doc_id AND s.section_id = gc.section_id AND s.sent_id = gc.sent_id AND gc.gene_wordidxs = s.gene_wordidxs AND gc.pheno_wordidxs = s.pheno_wordidxs) 
    JOIN genepheno_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    gc.expectation > 0.9 
    AND l.is_correct = 'f'
  GROUP BY labeler) fp
  JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT relation_id) tp
  FROM
    genepheno_causation_is_correct_inference gc 
    JOIN genepheno_holdout_set s 
      ON (s.doc_id = gc.doc_id AND s.section_id = gc.section_id AND s.sent_id = gc.sent_id AND gc.gene_wordidxs = s.gene_wordidxs AND gc.pheno_wordidxs = s.pheno_wordidxs) 
    JOIN genepheno_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    gc.expectation > 0.9 
    AND l.is_correct = 't'
  GROUP BY labeler) tp
  ON (fp.labeler = tp.labeler);
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} > /dev/stderr
rm -rf ${TMPDIR}
