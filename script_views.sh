#!/bin/sh

#This file is to be run in your original dd-genomics folder, the one you want data from.

cp db_for_gp.url db.url

deepdive redo weights

deepdive redo dd_inference_result_variables_mapped_weights_bis
deepdive sql "insert into dd_inference_result_variables_mapped_weights_bis select * from dd_inference_result_variables_mapped_weights;"

deepdive redo gene_mentions_views
deepdive redo genepheno_association_views
deepdive redo genepheno_causation_views
deepdive redo sentences_input_views
deepdive redo pheno_mentions_views

database_greenplum=$(cat db_for_gp.url | sed 's/.*:\/\/.*\///')

mkdir -p ../tables_for_views
export PATH=/dfs/scratch0/netj/postgresql/9.4.4/bin:$PATH
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t sentences_input_views > ../tables_for_views/sentences_input_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t gene_mentions_views > ../tables_for_views/gene_mentions_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t genepheno_causation_views > ../tables_for_views/genepheno_causation_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t pheno_mentions_views > ../tables_for_views/pheno_mentions_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t genepheno_association_views > ../tables_for_views/genepheno_association_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t gene_mentions_filtered_inference_label_inference > ../tables_for_views/gene_mentions_filtered_inference_label_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t genepheno_causation_inference_label_inference > ../tables_for_views/genepheno_causation_inference_label_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t genepheno_association_inference_label_inference > ../tables_for_views/genepheno_association_inference_label_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t dd_inference_result_variables > ../tables_for_views/dd_inference_result_variables.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t gene_mentions_filtered_inference > ../tables_for_views/gene_mentions_filtered_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t genepheno_causation_inference > ../tables_for_views/genepheno_causation_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t genepheno_association_inference > ../tables_for_views/genepheno_association_inference.sql



cp db_for_pg.url db.url

deepdive redo init/db
deepdive sql < ../tables_for_views/genepheno_causation_views.sql
deepdive sql < ../tables_for_views/sentences_input_views.sql 
deepdive sql < ../tables_for_views/genepheno_association_views.sql 
deepdive sql < ../tables_for_views/gene_mentions_views.sql 
deepdive sql < ../tables_for_views/pheno_mentions_views.sql 
deepdive sql < ../tables_for_views/dd_inference_result_variables.sql
deepdive sql < ../tables_for_views/gene_mentions_filtered_inference.sql 
deepdive sql < ../tables_for_views/gene_mentions_filtered_inference_label_inference.sql 
deepdive sql < ../tables_for_views/genepheno_causation_inference.sql 
deepdive sql < ../tables_for_views/genepheno_causation_inference_label_inference.sql 
deepdive sql < ../tables_for_views/genepheno_association_inference.sql 
deepdive sql < ../tables_for_views/genepheno_association_inference_label_inference.sql 

deepdive sql "update sentences_input_views set words = replace(words, '|^|', ' ');"


#? mindbender search drop
# # define which port to use for your own Elasticsearch instance launched internally by mindbender
export ELASTICSEARCH_BASEURL=http://localhost:9${RANDOM:0:3}

#this bulk batchsize could be increased to increase speed. Careful, from 200000, it starts not to work so well.
export ELASTICSEARCH_BULK_BATCHSIZE=20000
mindbender search update 

export ES_HEAP_SIZE=10g

PORT=$RANDOM mindbender search gui
