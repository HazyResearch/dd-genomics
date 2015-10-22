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
  false_pos,
  false_neg,
  true_neg,
  (true_pos + false_pos) positives,
  (true_neg + false_neg) negatives,
  (true_pos::float / (true_pos::float + false_pos::float)) as precision,
  (true_pos::float / (true_pos::float + false_neg::float)) as recall
FROM (
SELECT
  fp.labeler labeler,
  CASE WHEN tp.tp IS NULL THEN 0 ELSE tp.tp END true_pos,
  CASE WHEN fp.fp IS NULL THEN 0 ELSE fp.fp END false_pos,
  CASE WHEN fn.fn IS NULL THEN 0 ELSE fn.fn END false_neg,
  CASE WHEN tn.tn IS NULL THEN 0 ELSE tn.tn END true_neg
FROM
  (SELECT
    labeler,
    COUNT(DISTINCT mention_id) fp
  FROM
    gene_mentions_filtered_is_correct_inference g 
    JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    g.expectation > 0.9 
    AND l.is_correct = 'f'
  GROUP BY labeler) fp
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT mention_id) tp
  FROM
    gene_mentions_filtered_is_correct_inference g 
    JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    g.expectation > 0.9 
    AND l.is_correct = 't'
  GROUP BY labeler) tp
  ON (fp.labeler = tp.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT mention_id) fn
  FROM
    gene_mentions_filtered_is_correct_inference g 
    JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    g.expectation <= 0.9 
    AND l.is_correct = 't'
  GROUP BY labeler) fn
  ON (fp.labeler = fn.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT mention_id) tn
  FROM
    gene_mentions_filtered_is_correct_inference g 
    JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    g.expectation <= 0.9 
    AND l.is_correct = 'f'
  GROUP BY labeler) tn
  ON (fp.labeler = tn.labeler)) a;
EOF
psql -q -X --set ON_ERROR_STOP=1 -d $DB -f ${SQL_COMMAND_FILE} > /dev/stderr
rm -rf ${TMPDIR}

