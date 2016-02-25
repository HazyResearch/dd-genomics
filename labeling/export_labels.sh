#!/bin/bash -e

if [ $# -lt 1 ]; then
        echo "$0: ERROR: wrong number of arguments" >&2
        echo "$0: Please select a relation to export gene, pheno or genepheno" >&2
        echo "$0: USAGE: $0 {gene,pheno,genepheno,genepheno_causation_precision,genepheno_facts_precision,genepheno_multi_precision,genepheno_causation_50-75} OPTIONAL_NAME" >&2
        exit 1
fi

. ../env_local.sh

if [ -z $DDUSER ]
then
    echo "$0: Please set your DDUSER environemnt variable!"
    exit 1
fi

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
        	./extract_gene_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(mention_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT * FROM gene_labels gl WHERE (gl.mention_id,  gl.labeler) NOT IN (SELECT mention_id, labeler FROM tmp)'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE gene_labels'
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO gene_labels'
		cat tmp.tsv >> "labels/gene_$NAME"
		rm tmp.tsv
	done
elif [ $1 = 'gene_precision' ]; then
        for DIR in *-gene-holdout-high-precision.$NAME; do
                ./extract_gene_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(mention_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT * FROM gene_precision_labels gl WHERE (gl.mention_id,  gl.labeler) NOT IN (SELECT mention_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE gene_precision_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO gene_precision_labels'
                cat tmp.tsv >> "labels/gene_precision_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'pheno' ]; then
        for DIR in *-pheno-holdout.$NAME; do
                ./extract_pheno_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'  
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(mention_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'  
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT * FROM pheno_labels pl WHERE (pl.mention_id, pl.labeler) NOT IN (SELECT mention_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE pheno_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO pheno_labels'
		cat tmp.tsv >> "labels/pheno_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno' ]; then
        for DIR in *-genepheno-holdout.$NAME; do
                ./extract_genepheno_causation_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
		# UPDATE CAUSATION
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_causation_labels gl WHERE (gl.relation_id, gl.labeler) NOT IN (SELECT relation_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_causation_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_causation_labels'
                cat tmp.tsv >> "labels/genepheno_causation_$NAME"
                rm tmp.tsv
		# UPDATE ASSOCIATION
		./extract_genepheno_association_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
		psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_association_labels gl WHERE (gl.relation_id, gl.labeler) NOT IN (SELECT relation_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_association_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_association_labels'
                cat tmp.tsv >> "labels/genepheno_association_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno_causation_precision' ]; then
        for DIR in *-genepheno-holdout-high-expectation.$NAME; do
                ./extract_genepheno_causation_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                # UPDATE CAUSATION PRECISION
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_causation_precision_labels gl WHERE (gl.relation_id, gl.labeler) NOT IN (SELECT relation_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_causation_precision_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_causation_precision_labels'
                cat tmp.tsv >> "labels/genepheno_causation_precision_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno_facts_precision' ]; then
        for DIR in *-genepheno-facts-precision.$NAME; do
                ./extract_genepheno_causation_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_facts_precision_labels gl WHERE (gl.relation_id, gl.labeler) NOT IN (SELECT relation_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_facts_precision_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_facts_precision_labels'
                cat tmp.tsv >> "labels/genepheno_facts_precision_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno_multi_precision' ]; then
        for DIR in *-genepheno-multi-precision.$NAME; do
                ./extract_genepheno_causation_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_multi_precision_labels gl WHERE (gl.relation_id, gl.labeler) NOT IN (SELECT relation_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_multi_precision_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_multi_precision_labels'
                cat tmp.tsv >> "labels/genepheno_multi_precision_$NAME"
                rm tmp.tsv
        done
elif [ $1 = 'genepheno_causation_50-75' ]; then
        for DIR in *-genepheno-holdout-50-75.$NAME; do
                ./extract_genepheno_causation_labels_from_json.py $DIR/tags.json $NAME > tmp.tsv
                # UPDATE CAUSATION PRECISION
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE IF EXISTS tmp'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'CREATE TABLE tmp(relation_id text, is_correct boolean, labeler text, version int)'
                cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_labels -c 'COPY tmp FROM STDIN;'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'INSERT INTO tmp SELECT DISTINCT * FROM genepheno_causation_50_75_labels gl WHERE (gl.relation_id, gl.labeler) NOT IN (SELECT relation_id, labeler FROM tmp)'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'DROP TABLE genepheno_causation_50_75_labels'
                psql -U $DDUSER -p 6432 -d genomics_labels -c 'ALTER TABLE tmp RENAME TO genepheno_causation_50_75_labels'
                cat tmp.tsv >> "labels/genepheno_causation_50_75_$NAME"
                rm tmp.tsv
        done
else
        echo "Argument not valid"
        echo "$0: USAGE: $0 {gene,pheno,genepheno,genepheno_causation_precision,gene_precision,genepheno_facts_precision,genepheno_causation_50-75} OPTIONAL_NAME" >&2
        exit 1
fi

