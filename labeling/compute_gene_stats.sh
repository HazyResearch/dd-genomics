

#!/bin/bash

. ../env_local.sh

if [ $# -eq 1 ]; then
        echo "Setting confidence to $1"
        CONFIDENCE=$1
else
        echo "Setting confidence to 0.9"
        CONFIDENCE=0.9
fi

# extract all labels from the genepheno labels that are true
deepdive sql "COPY (SELECT gl.mention_id, gl.is_correct FROM gene_labels gl, gene_mentions_filtered gm WHERE gl.mention_id=gm.mention_id) TO STDOUT WITH NULL AS ''" > gene_labels.tsv

# extract all predictions from the genepheno_causation table
deepdive sql  "COPY (SELECT gi.mention_id, gi.expectation FROM gene_mentions_filtered_inference_label_inference gi, gene_labels gl WHERE gi.mention_id = gl.mention_id) TO STDOUT WITH NULL AS ''" > gene_predictions.tsv
# launch python script that computes precision and recall
./compute_stats_helper.py gene_labels.tsv gene_predictions.tsv $CONFIDENCE > stats_genes.tsv
rm gene_labels.tsv
rm gene_predictions.tsv
