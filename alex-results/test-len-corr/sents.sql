COPY(
SELECT
  r.relation_id,
  i.expectation,
  s.dep_paths
FROM
  genepheno_causation r,
  genepheno_causation_inference_label_inference i,
  sentences_input s
WHERE
  r.relation_id = i.relation_id
  AND r.doc_id = s.doc_id
  AND r.section_id = s.section_id
  AND r.sent_id = s.sent_id
) TO '/tmp/all_rel_sents.tsv' DELIMITER '\t';
