set -beEu -o pipefail

cd ..
source env_local.sh
deepdive sql """
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
    COUNT(DISTINCT s.doc_id) fp
  FROM
    gene_mentions_filtered_is_correct_inference g 
    RIGHT JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    COALESCE(g.expectation, 0) > 0.5 
    AND l.is_correct = 'f'
  GROUP BY labeler) fp
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT s.doc_id) tp
  FROM
    gene_mentions_filtered_is_correct_inference g 
    RIGHT JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    COALESCE(g.expectation, 0) > 0.5 
    AND l.is_correct = 't'
  GROUP BY labeler) tp
  ON (fp.labeler = tp.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT s.doc_id) fn
  FROM
    gene_mentions_filtered_is_correct_inference g 
    RIGHT JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    COALESCE(g.expectation, 0) <= 0.5 
    AND l.is_correct = 't'
  GROUP BY labeler) fn
  ON (fp.labeler = fn.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT s.doc_id) tn
  FROM
    gene_mentions_filtered_is_correct_inference g 
    RIGHT JOIN gene_holdout_set s 
      ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|^|'))::int[] = s.gene_wordidxs) 
    JOIN gene_holdout_labels l
      ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  WHERe
    COALESCE(g.expectation, 0) <= 0.5 
    AND l.is_correct = 'f'
  GROUP BY labeler) tn
  ON (fp.labeler = tn.labeler)) a;
"""
