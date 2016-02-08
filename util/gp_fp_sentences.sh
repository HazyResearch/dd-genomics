#!/bin/bash -e
set -beEu -o pipefail

cd ..
source env_local.sh
deepdive sql """
COPY (
SELECT DISTINCT
  s.labeler CAUSATION_FALSE_POSITIVES,
  si.doc_id,
  si.section_id,
  si.sent_id,
  gc.gene_name,
  gc.gene_wordidxs,
  gc.pheno_wordidxs,
  (string_to_array(si.words, '|^|'))[(gc.pheno_wordidxs)[1] + 1] first_pheno,
  array_to_string(string_to_array(si.words, '|^|'), ' ') words,
  array_to_string(string_to_array(si.lemmas, '|^|'), ' ') lemmas

FROM
  genepheno_causation_is_correct_inference gc 
  RIGHT JOIN genepheno_causation_labels s 
    ON (s.relation_id = gc.relation_id)
  JOIN sentences_input si
    ON (si.doc_id = gc.doc_id AND si.section_id = gc.section_id AND si.sent_id = gc.sent_id)
WHERE
  COALESCE(gc.expectation, 0) > 0.9 
  AND s.is_correct = 'f') TO STDOUT;
"""
