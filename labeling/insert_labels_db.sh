#!/bin/bash

if [ $# -lt 1 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: Please select a relation to export gene, pheno or genepheno" >&2
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

source ../env_local.sh
if [ $1 = 'gene' ]; then
	psql -U $DDUSER -p 6432 -d genomics-labels -c 'COPY '
elif [ $1 = 'pheno' ]; then
        for DIR in *-pheno-holdout.$NAME; do
                ./export_pheno_labels.py $DIR/tags.json $NAME
        done
elif [ $1 = 'genepheno' ]; then
        for DIR in *-genepheno-holdout.$NAME; do
                ./export_genepheno_labels.py $DIR/tags.json $NAME
        done
else    
        echo "Argument not valid"
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi
