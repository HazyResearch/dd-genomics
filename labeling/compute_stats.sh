#!/bin/bash

. ../env_local.sh

# extract all labels from the genepheno labels that are true
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM genepheno_labels) TO STDOUT WITH NULL AS ''" > genepheno_labels.tsv

# extract all predictions from the genepheno_causation table
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM genepheno_labels) TO STDOUT WITH NULL AS ''" > genepheno_predictions.tsv



