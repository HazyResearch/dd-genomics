COPY(
SELECT
  gf.feature,
  gc.is_correct,
  COUNT(*)
FROM
  genepheno_features gf,
  genepheno_causation gc
WHERE
  gf.relation_id = gc.relation_id
  AND gc.is_correct IS NOT NULL
GROUP BY
  gf.feature, gc.is_correct
) TO '/tmp/chi-sq-gp.tsv' DELIMITER '\t';
