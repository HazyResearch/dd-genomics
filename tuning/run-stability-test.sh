#!/bin/bash

if [ $# -lt 4 ]; then
  echo "$0: USAGE: $0 LEARN_EPOCHS INFER_EPOCHS SAMPLES_PER_LEARN LEARN|INFER" >&2
  exit 1
fi

source ../env_local.sh

# replace the sampler args & recompile
eval "sed -i 's/n_learning_epoch [0-9]*/n_learning_epoch $1/g' ../deepdive.conf"
eval "sed -i 's/n_inference_epoch [0-9]*/n_inference_epoch $2/g' ../deepdive.conf"
eval "sed -i 's/n_samples_per_learning_epoch [0-9]*/n_samples_per_learning_epoch $3/g' ../deepdive.conf"
deepdive compile

# Silence deepdive do editor edit mode
export DEEPDIVE_PLAN_EDIT=false

echo "$4 -- Learning epochs=$1, inference epochs=$2, samples-per-learning=$3:"

# RUN #1 - Must do deepdive model learn as infer does nothing
deepdive model learn

# Store weights and marginals
deepdive sql < save-tables-for-stability-stats.sql

# RUN #2 - if running "infer", save and reuse weights to skip learning
if [ "$4" = "infer" ]; then
  echo "Reusing weights..."
  deepdive model weights keep
  deepdive model weights reuse
fi
eval "deepdive model $4"

# Get difference stats
echo "# $4 -- Learning epochs=$1, inference epochs=$2, samples-per-learning=$3:" >> stability.tsv
deepdive sql < stability-stats.sql >> stability.tsv
