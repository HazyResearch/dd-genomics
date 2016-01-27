#!/bin/bash

. ../env_local.sh

echo "Exporting genepheno causation"
./convert_old_gp_labels.py ../onto/manual/genepheno_holdout_labels_caus.tsv > tmp.tsv
cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY genepheno_causation_labels FROM STDIN;'
rm tmp.tsv

echo "Exporting genepheno association"
./convert_old_gp_labels.py ../onto/manual/genepheno_holdout_labels_assoc.tsv > tmp.tsv
cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY genepheno_association_labels FROM STDIN;'
rm tmp.tsv

