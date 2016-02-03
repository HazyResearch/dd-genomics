#!/bin/bash -e
set -beEu -o pipefail

cd ..
source env_local.sh
deepdive sql """
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
    COUNT(DISTINCT s.relation_id) fp
  FROM
    genepheno_association_is_correct_inference gc 
    RIGHT JOIN genepheno_association_labels s 
      ON (gc.relation_id = s.relation_id)
  WHERe
    COALESCE(gc.expectation, 0) > 0.5 
    AND s.is_correct = 'f'
  GROUP BY labeler) fp
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT s.relation_id) tp
  FROM
    genepheno_association_is_correct_inference gc 
    RIGHT JOIN genepheno_association_labels s 
      ON (s.relation_id = gc.relation_id)
  WHERe
    COALESCE(gc.expectation, 0) > 0.5 
    AND s.is_correct = 't'
  GROUP BY labeler) tp
  ON (tp.labeler = fp.labeler)
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT s.relation_id) fn
  FROM
    genepheno_association_is_correct_inference gc 
    RIGHT JOIN genepheno_association_labels s 
      ON (s.relation_id = gc.relation_id)
  WHERe
    COALESCE(gc.expectation, 0) <= 0.5
    AND s.is_correct = 't'
  GROUP BY labeler) fn
  ON (fn.labeler = COALESCE(fp.labeler, tp.labeler))
  FULL OUTER JOIN
  (SELECT
    labeler,
    COUNT(DISTINCT s.relation_id) tn
  FROM
    genepheno_association_is_correct_inference gc 
    RIGHT JOIN genepheno_association_labels s 
      ON (s.relation_id = gc.relation_id)
  WHERe
    COALESCE(gc.expectation, 0) <= 0.5
    AND s.is_correct = 'f'
  GROUP BY labeler) tn
  ON (tn.labeler = COALESCE(fp.labeler, tp.labeler, fn.labeler))) a;
"""
