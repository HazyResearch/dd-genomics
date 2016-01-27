#!/bin/bash

if [ $# -lt 1 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: Please select a relation to export gene, pheno or genepheno" >&2
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

. ../env_local.sh

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
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(mention_id text, is_correct text, labeler text)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT * FROM gene_labels gl WHERE (gl.mention_id, gl.is_correct, gl.labeler) NOT IN (SELECT * FROM tmp)'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE gene_labels'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO gene_labels'

		cat tmp.tsv >> "labels/gene_$NAME"
		rm tmp.tsv
	done
elif [ $1 = 'pheno' ]; then
        for DIR in *-pheno-holdout.$NAME; do
                ./extract_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'  
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(mention_id text, is_correct text, labeler text)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'  
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT * FROM pheno_labels pl WHERE (pl.mention_id, pl.is_correct, pl.labeler) NOT IN (SELECT * FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE pheno_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO pheno_labels'
		cat tmp.tsv >> "labels/pheno_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno' ]; then
        for DIR in *-genepheno-holdout.$NAME; do
                ./extract_genepheno_causation_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
	#	cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY genepheno_causation_labels FROM STDIN;'
		# UPDATE CAUSATION
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct text, labeler text)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_causation_labels gl WHERE (gl.relation_id) NOT IN (SELECT relation_id FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_causation_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_causation_labels'
                cat tmp.tsv >> "labels/genepheno_causation_$NAME"
                rm tmp.tsv
		# UPDATE ASSOCIATION
		./extract_genepheno_association_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct text, labeler text)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_association_labels gl WHERE (gl.relation_id) NOT IN (SELECT relation_id FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_association_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_association_labels'
               cat tmp.tsv >> "labels/genepheno_association_$NAME"
               rm tmp.tsv
        done
else
        echo "Argument not valid"
        echo "$0: USAGE: $0 {gene,pheno,genepheno} OPTIONAL_NAME" >&2
        exit 1
fi

