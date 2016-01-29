#!/bin/bash

. ../env_local.sh

if [ $# -eq 1 ]; then
        echo "Setting confidence to $1"
        CONFIDENCE=$1
else
        echo "Setting confidence to 0.9"
        CONFIDENCE=.9
fi

# extract all labels from the genepheno labels that are true
deepdive sql "COPY (SELECT gal.relation_id, gal.is_correct, gal.labeler FROM genepheno_causation_labels gal, genepheno_pairs gp WHERE (gp.gene_mention_id || ('_' || gp.pheno_mention_id)) = gal.relation_id) TO STDOUT WITH NULL AS ''" > genepheno_causation_labels.tsv

# extract all predictions from the genepheno_causation table
deepdive sql "COPY (SELECT gi.relation_id, gi.expectation FROM genepheno_causation_inference_label_inference gi, genepheno_causation_labels gal WHERE gal.relation_id = gi.relation_id) TO STDOUT WITH NULL AS ''" > genepheno_causation_predictions.tsv
# launch python script that computes precision and recall
./compute_stats_helper.py genepheno_causation_labels.tsv genepheno_causation_predictions.tsv $CONFIDENCE > stats_causation.tsv
#rm genepheno_causation_labels.tsv
#rm genepheno_causation_predictions.tsv

