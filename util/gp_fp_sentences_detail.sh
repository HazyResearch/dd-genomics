#!/bin/bash -e
set -beEu -o pipefail

cd ..
source env_local.sh
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
  AND s.is_correct = 'f') TO STDOUT;
""" | while read rid
do
  echo $i
done
