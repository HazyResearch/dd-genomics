#!/bin/bash -e
set -beEu -o pipefail

echo "CREATE HOLDOUT PATCH!"


if [ $# -eq 1 ]
then
  version_string="AND version = $1"
else
  version_string=""
fi

GP_CUTOFF=`cat ../results_log/gp_cutoff`

cd ..
source env_local.sh
deepdive sql """
COPY (
SELECT DISTINCT
  s.labeler CAUSATION_TRUE_POSITIVES,
  si.doc_id,
  si.section_id,
  si.sent_id,
  gc.gene_name,
  gc.gene_wordidxs,
  gc.pheno_wordidxs,
  sv.supertype
FROM
  genepheno_causation_all_superv sv
  JOIN genepheno_causation_is_correct_inference gc 
    on (sv.relation_id = gc.relation_id)
  RIGHT JOIN genepheno_causation_labels s 
    ON (s.relation_id = gc.relation_id)
  JOIN sentences_input si
    ON (si.doc_id = gc.doc_id AND si.section_id = gc.section_id AND si.sent_id = gc.sent_id)
WHERE
  COALESCE(gc.expectation, 0) > $GP_CUTOFF 
  AND s.is_correct = 'f'
  $version_string) TO STDOUT;
"""
