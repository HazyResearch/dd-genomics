#!/bin/sh

#This file is to be run in your original dd-genomics folder, the one you want data from.

if [ "$#" -ne 1 ] ; then
  echo "Usage: $0 name_database_you_want_data_from" >&2
  exit 1
fi

deepdive compile

deepdive do weights

deepdive do dd_inference_result_variables_mapped_weights_bis
deepdive sql "insert into dd_inference_result_variables_mapped_weights_bis select * from dd_inference_result_variables_mapped_weights;"

deepdive do gene_mentions_views
deepdive do genepheno_association_views
deepdive do genepheno_causation_views
deepdive do sentences_input_views
deepdive do pheno_mentions_views

cd ..
mkdir -p tables_for_views
cd tables_for_views
export PATH=/dfs/scratch0/netj/postgresql/9.4.4/bin:$PATH
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t sentences_input_views > sentences_input_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t gene_mentions_views > gene_mentions_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t genepheno_causation_views > genepheno_causation_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t pheno_mentions_views > pheno_mentions_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t genepheno_association_views > genepheno_association_views.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t gene_mentions_filtered_inference_label_inference > gene_mentions_filtered_inference_label_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t genepheno_causation_inference_label_inference > genepheno_causation_inference_label_inference.sql                            
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t genepheno_association_inference_label_inference > genepheno_association_inference_label_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t dd_inference_result_variables > dd_inference_result_variables.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t gene_mentions_filtered_inference > gene_mentions_filtered_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t genepheno_causation_inference > genepheno_causation_inference.sql
pg_dump -p 6432 -h raiders7 -U tpalo $1 -t genepheno_association_inference > genepheno_association_inference.sql



cd ../dd-genomics_for_views
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

#Trial to increase the number of buckets and make views work
export ELASTICSEARCH_BULK_BATCHSIZE=200000
mindbender search update 

export ES_HEAP_SIZE=10g

PORT=$RANDOM mindbender search gui