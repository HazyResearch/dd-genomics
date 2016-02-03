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
        echo "Setting confidence to 0.9"
        CONFIDENCE=0.9
fi

# extract all labels from the genepheno labels that are true
deepdive sql "COPY (SELECT gl.mention_id, gl.is_correct, gl.labeler FROM gene_labels gl, gene_mentions_filtered gm WHERE gl.mention_id=gm.mention_id AND gl.version=$VERSION) TO STDOUT WITH NULL AS ''" > gene_labels.tsv

# extract all predictions from the genepheno_causation table
deepdive sql  "COPY (SELECT gi.mention_id, gi.expectation FROM gene_mentions_filtered_inference_label_inference gi, gene_labels gl WHERE gi.mention_id = gl.mention_id AND gl.version=$VERSION) TO STDOUT WITH NULL AS ''" > gene_predictions.tsv
# launch python script that computes precision and recall
$GDD_HOME/results_log/compute_stats_helper.py gene_labels.tsv gene_predictions.tsv $CONFIDENCE > $GDD_HOME/results_log/latest_stats_genes.tsv
rm gene_labels.tsv
rm gene_predictions.tsv

if [ $# -eq 3 ] && [ $3 = 'OPTOUT' ]; then
        echo "NO LOGGING"
        exit 0
fi

# Store logs
DIR_NAME=$GDD_HOME/results_log/$DDUSER/genes-`date +'%m-%d-%Y-%H-%M-%S'`
mkdir -p $DIR_NAME

# Store stats in log
cat $GDD_HOME/results_log/latest_stats_genes.tsv > $DIR_NAME/stats_genes.tsv

# Store TP/FP/TN/FN
# TP is trivial, we just need to see where we have true label with confidence > $CONFIDENCE
deepdive sql "COPY (SELECT gl.mention_id, gl.is_correct, gl.labeler, gi.expectation FROM gene_labels gl, gene_mentions_filtered_inference_label_inference gi WHERE gl.mention_id = gi.mention_id AND gi.expectation >= $CONFIDENCE AND gl.is_correct = 't' AND gl.version=$VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/TP.tsv

# FP is symmetric with label 'f'
deepdive sql "COPY (SELECT gl.mention_id, gl.is_correct, gl.labeler, gi.expectation FROM gene_labels gl, gene_mentions_filtered_inference_label_inference gi WHERE gl.mention_id = gi.mention_id AND 
gi.expectation >= $CONFIDENCE AND gl.is_correct = 'f' AND gl.version=$VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/FP.tsv

# FN 
deepdive sql "COPY (SELECT gl.mention_id, gl.is_correct, gl.labeler, gi.expectation FROM gene_labels gl, gene_mentions_filtered_inference_label_inference gi WHERE gl.mention_id = gi.mention_id AND gi.expectation < $CONFIDENCE AND gl.is_correct = 't' AND gl.version=$VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/FN.tsv

# STORE holdout set
deepdive sql "COPY (SELECT * FROM gene_labels WHERE version=$VERSION) TO STDOUT WITH NULL AS ''" > $DIR_NAME/holdout_set.tsv

# STORE a path to sentences_input used + count
echo '/dfs/scratch0/genomics-data/sentences_input_v0.sql' > $DIR_NAME/input_data
deepdive sql "COPY (SELECT count(*) FROM sentences_input) TO STDOUT WITH NULL AS ''" >> $DIR_NAME/input_data
