#!/bin/bash

. ../env_local.sh

if [ $# -eq 1 ]; then
        echo "Setting confidence to $1"
        CONFIDENCE=$1
else
        echo "Setting confidence to 0.5"
        CONFIDENCE=.5
fi

# extract all labels from the genepheno labels that are true
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM genepheno_causation_labels) TO STDOUT WITH NULL AS ''" > genepheno_causation_labels.tsv

# extract all predictions from the genepheno_causation table
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c "COPY (SELECT relation_id, expectation FROM genepheno_causation_inference_label_inference) TO STDOUT WITH NULL AS ''" > genepheno_causation_predictions.tsv
# launch python script that computes precision and recall
./compute_stats_helper.py genepheno_causation_labels.tsv genepheno_causation_predictions.tsv $CONFIDENCE > stats_causation.tsv
rm genepheno_causation_labels.tsv
rm genepheno_causation_predictions.tsv

