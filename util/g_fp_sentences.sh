#!/bin/bash -e
set -beEu -o pipefail

echo "CREATE HOLDOUT PATCH!"


G_CUTOFF=`cat ../results_log/g_cutoff`

cd ..
source env_local.sh
deepdive sql """
COPY (
SELECT DISTINCT
  l.labeler GENE_FALSE_POSITIVES,
  l.doc_id,
  l.section_id,
  l.sent_id,
  g.expectation,
  g.gene_name,
  s.gene_wordidxs,
  (string_to_array(si.words, '|^|'))[s.gene_wordidxs[1] + 1],
  array_to_string(string_to_array(si.words, '|^|'), ' ') words,
  array_to_string(string_to_array(si.lemmas, '|^|'), ' ') lemmas
FROM
  gene_mentions_filtered_is_correct_inference g 
  RIGHT JOIN gene_holdout_set s 
    ON (s.doc_id = g.doc_id AND s.section_id = g.section_id AND s.sent_id = g.sent_id AND (STRING_TO_ARRAY(g.wordidxs, '|~|'))::int[] = s.gene_wordidxs) 
  JOIN gene_holdout_labels l
    ON (s.doc_id = l.doc_id AND s.section_id = l.section_id AND s.sent_id = l.sent_id) 
  JOIN sentences_input si
    ON (si.doc_id = l.doc_id AND si.section_id = l.section_id AND si.sent_id = l.sent_id)
WHERE
  COALESCE(g.expectation, 0) > $G_CUTOFF 
  AND l.is_correct = 'f') TO STDOUT;
"""
