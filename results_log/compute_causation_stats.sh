#!/bin/bash

. $GDD_HOME/env_local.sh

if [ $# -ge 1 ]; then
        echo "Setting version to $1"
        VERSION=$1
else
        echo "Setting version to 0"
        VERSION=0
fi

if [ $# -ge 2 ]; then
        echo "Setting confidence to $2"
        CONFIDENCE=$2
else
        cutoff=`cat ${GDD_HOME}/results_log/gp_cutoff`
        echo "Setting confidence to $cutoff"
        CONFIDENCE=$cutoff
fi

# extract all labels from the genepheno labels that are true
deepdive sql "COPY (SELECT gal.relation_id, gal.is_correct, gal.labeler FROM genepheno_causation_labels gal, genepheno_pairs gp WHERE (gp.gene_mention_id || ('_' || gp.pheno_mention_id)) = gal.relation_id AND gal.version = $VERSION) TO STDOUT WITH NULL AS ''" > genepheno_causation_labels.tsv

# extract all predictions from the genepheno_causation table
deepdive sql "COPY (SELECT gi.relation_id, gi.expectation FROM genepheno_causation_inference_label_inference gi, genepheno_causation_labels gal WHERE gal.relation_id = gi.relation_id AND gal.version = $VERSION) TO STDOUT WITH NULL AS ''" > genepheno_causation_predictions.tsv
# launch python script that computes precision and recall
$GDD_HOME/results_log/compute_stats_helper.py genepheno_causation_labels.tsv genepheno_causation_predictions.tsv $CONFIDENCE > $GDD_HOME/results_log/latest_stats_causation.tsv
rm genepheno_causation_labels.tsv
rm genepheno_causation_predictions.tsv

if [ $# -eq 3 ] && [ $3 = 'OPTOUT' ]; then
        echo"NO LOGGING"
        exit 0
fi

# Store logs
DIR_NAME=$GDD_HOME/results_log/$DDUSER/causation-`date +'%m-%d-%Y-%H-%M-%S'`
mkdir -p $DIR_NAME

# Store stats in log
cat $GDD_HOME/results_log/latest_stats_causation.tsv > $DIR_NAME/stats_causation.tsv

# Store TP/FP/TN/FN
# TP is trivial, we just need to see where we have true label with confidence > $CONFIDENCE
deepdive sql "COPY (SELECT gal.relation_id, gal.is_correct, gal.labeler, gi.expectation  FROM genepheno_causation_labels gal, genepheno_causation_inference_label_inference gi WHERE gal.relation_id = gi.relation_id AND gi.expectation >= $CONFIDENCE AND gal.is_correct = 't' AND gal.version = $VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/TP.tsv

# FP is a bit more complex since we need to join with genepheno_pairs to avoid FP on documents that we are ejecting (cancer suff)
deepdive sql "COPY (SELECT gal.relation_id, gal.is_correct, gal.labeler, gi.expectation  FROM genepheno_causation_labels gal, genepheno_causation_inference_label_inference gi, genepheno_pairs gp WHERE gal.relation_id = gi.relation_id AND gi.expectation >= $CONFIDENCE AND gal.is_correct = 'f' AND (gp.gene_mention_id || ('_' || gp.pheno_mention_id)) = gal.relation_id AND gal.version = $VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/FP.tsv

# FN is tricky because we include: 1- relations labeled True having < confidence in inference. AND 2- relations that have TRUE label in labels that are in genepheno_pairs but are not in inference table 
# 1
deepdive sql "COPY (SELECT gal.relation_id, gal.is_correct, gal.labeler, gi.expectation  FROM genepheno_causation_labels gal, genepheno_causation_inference_label_inference gi, genepheno_pairs gp WHERE gal.relation_id = gi.relation_id AND gi.expectation < $CONFIDENCE AND gal.is_correct = 't' AND (gp.gene_mention_id || ('_' || gp.pheno_mention_id)) = gal.relation_id AND gal.version = $VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/FN.tsv
# 2
deepdive sql "COPY (SELECT gal.relation_id, gal.is_correct, gal.labeler, 'NA' FROM genepheno_causation_labels gal 
JOIN genepheno_pairs gp ON (gp.gene_mention_id || ('_' || gp.pheno_mention_id)) = gal.relation_id
LEFT JOIN genepheno_causation_inference_label_inference gi ON gal.relation_id = gi.relation_id
WHERE gi.relation_id IS NULL AND gal.is_correct='t' AND gal.version = $VERSION) TO STDOUT WITH NULL AS ''" >> $DIR_NAME/FN.tsv

# STORE holdout set
deepdive sql "COPY (SELECT * FROM genepheno_causation_labels gal WHERE gal.version = $VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/holdout_set.tsv

# STORE a path to sentences_input used + count
echo '/dfs/scratch0/genomics-data/sentences_input_v0.sql' > $DIR_NAME/input_data
deepdive sql "COPY (SELECT count(*) FROM sentences_input) TO STDOUT WITH NULL AS ''" >> $DIR_NAME/input_data




