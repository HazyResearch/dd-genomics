#!/bin/bash

if [ $# -lt 3 ]; then
  echo "$0: USAGE: $0 n_learning_epoch n_inference_epoch n_samples_per_learning_epoch" >&2
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

# RUN #1
deepdive model learn

# Store results, RUN #2
deepdive sql < save-tables-for-stability-stats.sql
deepdive model learn

# Get difference stats
deepdive sql < stability-stats.sql
