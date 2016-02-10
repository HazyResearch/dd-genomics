#!/bin/bash -e
set -beEu -o pipefail

if [ $# -eq 1 ]
then
  version_string="AND version = $1"
else
  version_string=""
fi

cd ..
source env_local.sh

#deepdive sql """
#drop table weights;
#create table weights as (select * from dd_inference_result_variables_mapped_weights) distributed by (id);
#"""

deepdive sql """
COPY (
SELECT DISTINCT
  gc.relation_id
FROM
  genepheno_causation_is_correct_inference gc 
  RIGHT JOIN (select distinct * from
      ((select * from genepheno_causation_labels)
      union (select * from genepheno_causation_precision_labels)) a) s
    ON (s.relation_id = gc.relation_id)
WHERE
  COALESCE(gc.expectation, 0) > 0.9 
  AND s.is_correct = 'f'
  $version_string) TO STDOUT;
""" | while read rid
do
echo "BASE INFO"
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
  RIGHT JOIN (select distinct * from
      ((select * from genepheno_causation_labels)
      union (select * from genepheno_causation_precision_labels)) a) s
    ON (s.relation_id = gc.relation_id)
  JOIN sentences_input si
    ON (si.doc_id = gc.doc_id AND si.section_id = gc.section_id AND si.sent_id = gc.sent_id)
WHERE
  gc.relation_id = '$rid'
  AND COALESCE(gc.expectation, 0) > 0.9
  AND s.is_correct = 't') TO STDOUT;
""" 
echo "DISTANT SUPERVISION"
deepdive sql """
COPY (
SELECT DISTINCT
  gc.supertype, gc.subtype
FROM
  genepheno_causation gc
WHERE
  gc.relation_id = '$rid') TO STDOUT
""" 
echo "FEATURES"
deepdive sql """
select distinct
  feature,
  w.weight
from 
  genepheno_relations r 
  join genepheno_features f 
    on (f.relation_id = r.relation_id) 
  join weights w 
    on (w.description = ('inf_istrue_genepheno_causation_inference--' || f.feature)) 
where 
  r.relation_id = '$rid'
  AND abs(w.weight) > 0
order by abs(weight) desc
limit 25;
"""

done
