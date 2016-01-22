#!/bin/bash

if [ $# -lt 1 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: Please select a relation to export gene, pheno or genepheno" >&2
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

source ../env_local.sh

if [ $# -eq 2 ]; then
        echo "Setting name to $2"
        NAME=$2
else
        echo "Setting name to default $DDUSER"
        NAME=$DDUSER
fi

echo "Exporting labels"
if [ $1 = 'gene' ]; then
        for DIR in *-gene-holdout.$NAME; do
        	./extract_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY gene_labels FROM STDIN;'
		cat tmp.tsv >> "labels/gene_$NAME"
		rm tmp.tsv
	done
elif [ $1 = 'pheno' ]; then
        for DIR in *-pheno-holdout.$NAME; do
                ./extract_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY pheno_labels FROM STDIN;'
                cat tmp.tsv >> "labels/pheno_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno' ]; then
        for DIR in *-genepheno-holdout.$NAME; do
                ./extract_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
		cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY genepheno_labels FROM STDIN;'
                cat tmp.tsv >> "labels/genepheno_$NAME"
                rm tmp.tsv
        done
else
        echo "Argument not valid"
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

