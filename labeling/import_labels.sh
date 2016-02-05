#/usr/bin/bash

. ../env_local.sh

# import remote tables to local DB using tmp files

# Start by causation labels
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM genepheno_causation_labels) TO STDOUT WITH NULL AS ''" > tmp.tsv 
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'DROP TABLE IF EXISTS genepheno_causation_labels'
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'CREATE TABLE genepheno_causation_labels(relation_id VARCHAR, is_correct VARCHAR, labeler VARCHAR, version int)'
cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'COPY genepheno_causation_labels FROM STDIN;'
rm tmp.tsv

# now do association
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM genepheno_association_labels) TO STDOUT WITH NULL AS ''" > tmp.tsv  
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'DROP TABLE IF EXISTS genepheno_association_labels'  
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'CREATE TABLE genepheno_association_labels(relation_id VARCHAR, is_correct VARCHAR, labeler VARCHAR, version int)'  
cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'COPY genepheno_association_labels FROM STDIN;' 
rm tmp.tsv

# now do genes
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM gene_labels) TO STDOUT WITH NULL AS ''" > tmp.tsv                       
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'DROP TABLE IF EXISTS gene_labels'
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'CREATE TABLE gene_labels(mention_id VARCHAR, is_correct VARCHAR, labeler VARCHAR, version int)'
cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'COPY gene_labels FROM STDIN;'
rm tmp.tsv

# now do pheno
psql -U $DDUSER -p 6432 -d genomics_labels -c "COPY (SELECT * FROM pheno_labels) TO STDOUT WITH NULL AS ''" > tmp.tsv                       
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'DROP TABLE IF EXISTS pheno_labels'
psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'CREATE TABLE pheno_labels(relation_id VARCHAR, is_correct VARCHAR, labeler VARCHAR, version int)'
cat tmp.tsv | psql -U $DDUSER -p 6432 -d genomics_$DDUSER -c 'COPY pheno_labels FROM STDIN;'
rm tmp.tsv


