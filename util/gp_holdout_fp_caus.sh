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
  labeler,
  true_pos,
  true_neg,
  false_pos,
  false_neg,
  (true_pos::float / CASE WHEN (true_pos::float + false_pos::float) <> 0 THEN (true_pos::float + false_pos::float) ELSE 1 END) as precision,
  (true_pos::float / CASE WHEN (true_pos::float + false_neg::float) <> 0 THEN (true_pos::float + false_neg::float) ELSE 1 END) as recall
FROM (
SELECT
  COALESCE(fp.labeler, tp.labeler, fn.labeler, tn.labeler) labeler,
  CASE WHEN tp.tp IS NULL THEN 0 ELSE tp.tp END true_pos,
  CASE WHEN fp.fp IS NULL THEN 0 ELSE fp.fp END false_pos,
  CASE WHEN fn.fn IS NULL THEN 0 ELSE fn.fn END false_neg,
  CASE WHEN tn.tn IS NULL THEN 0 ELSE tn.tn END true_neg
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
  FULL OUTER JOIN
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
  ON (fp.labeler = tp.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT relation_id) fn
  FROM
    genepheno_causation_is_correct_inference gc 
    JOIN genepheno_holdout_set s 
      ON (s.doc_id = gc.doc_id AND s.section_id = gc.section_id AND s.sent_id = gc.sent_id AND gc.gene_wordidxs = s.gene_wordidxs AND gc.pheno_wordidxs = s.pheno_wordidxs) 
    JOIN genepheno_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    gc.expectation <= 0.9
    AND l.is_correct = 't'
  GROUP BY labeler) fn
  ON (tp.labeler = fn.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT relation_id) tn
  FROM
    genepheno_causation_is_correct_inference gc 
    JOIN genepheno_holdout_set s 
      ON (s.doc_id = gc.doc_id AND s.section_id = gc.section_id AND s.sent_id = gc.sent_id AND gc.gene_wordidxs = s.gene_wordidxs AND gc.pheno_wordidxs = s.pheno_wordidxs) 
    JOIN genepheno_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    gc.expectation <= 0.9
    AND l.is_correct = 'f'
  GROUP BY labeler) tn
  ON (fn.labeler = tn.labeler)) a;
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} > /dev/stderr
rm -rf ${TMPDIR}

