#!/bin/bash
source ../env_local.sh
true_pos=`psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} -c 'COPY (SELECT COUNT(*) FROM genepheno_facts_is_correct_inference WHERE expectation > 0.9 AND is_correct = true) TO STDOUT'`
false_pos=`psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} -c 'COPY (SELECT COUNT(*) FROM genepheno_facts_is_correct_inference WHERE expectation > 0.9 AND is_correct <> true) TO STDOUT'`
false_neg=`psql -X --set ON_ERROR_STOP=1 -d ${DBNAME} -c 'COPY (SELECT COUNT(*) FROM genepheno_facts_is_correct_inference WHERE expectation <= 0.9 AND is_correct = true) TO STDOUT'`
precision=$(echo "$true_pos / ($true_pos + $false_pos)" | bc -l)
recall=$(echo "$true_pos / ($true_pos + $false_neg)" | bc -l)
echo "Precision: $true_pos/$((true_pos + false_pos)) = $precision"
echo "Recall: $true_pos/$((true_pos + false_neg)) = $recall"
