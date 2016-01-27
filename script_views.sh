#!/bin/sh

#This file is to be run in your original dd-genomics folder, the one you want data from.

while true; do
    read -p "Have you checked deepdive and mindbender are correctly installed ?" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo 'In your deepdive folder, you can run the following commands';
                                echo 'git pull';
                                echo 'git checkout master';
                                echo 'git pull';
                                echo 'git submodule update --init';
                                echo 'make';
                                echo 'make install #PREFIX=...';
                                echo 'cd util/mindbender';
                                echo 'git submodule update --init';
                                echo 'cd ../..';
                                echo 'make build-mindbender install #PREFIX=/lfs/raiders7/0/tpalo/local';
                                exit;;
        * ) echo "Please answer y or n.";;
    esac
done
echo 

while true; do
    read -p "Is sentences_input the same as for the previous run of this script? Answer no only if you modified sentences_input or if it's the first time you run this script." yn
    case $yn in
        [Yy]* ) sentences_to_be_re_run=$false; break;;
        [Nn]* ) sentences_to_be_re_run=$true; break;;
        * ) echo "Please answer y or n.";;
    esac
done
echo 

if [[ ( -f db_for_gp.url)  ]]
then
        cp db_for_gp.url db.url
fi
if [[ ( -f db.url)  ]]
then
        cp db.url db_for_gp.url
fi
database_greenplum=$(cat db_for_gp.url | sed 's/.*:\/\/.*\///')
# Thomas own database in case 5432 doesn't work:
# echo "postgresql://localhost:15193/${database_greenplum}_for_views" > db_for_pg.url
echo "postgresql://localhost:5432/${database_greenplum}_for_views" > db_for_pg.url

deepdive redo weights
deepdive redo dd_inference_result_variables_mapped_weights_bis
deepdive sql "insert into dd_inference_result_variables_mapped_weights_bis select * from dd_inference_result_variables_mapped_weights;"

if [ $sentences_to_be_re_run]
then   
    deepdive mark todo sentences_input_views
else
    deepdive mark done sentences_input_views
fi

deepdive mark todo gene_mentions_views
deepdive mark todo genepheno_association_views
deepdive mark todo genepheno_causation_views
deepdive mark todo pheno_mentions_views

deepdive redo dumb_for_views

database_greenplum=$(cat db_for_gp.url | sed 's/.*:\/\/.*\///')

mkdir -p ../tables_for_views
export PATH=/dfs/scratch0/netj/postgresql/9.4.4/bin:$PATH

if [ $sentences_to_be_re_run]
then   
    pg_dump -p 6432 -h raiders7 -U tpalo ${database_greenplum} -t sentences_input_views > ../tables_for_views/sentences_input_views.sql
fi

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

if [ $sentences_to_be_re_run]
then   
    deepdive redo init/db
    deepdive sql < ../tables_for_views/sentences_input_views.sql 
    deepdive sql "update sentences_input_views set words = replace(words, '|^|', ' ');"
fi

deepdive sql < ../tables_for_views/genepheno_causation_views.sql
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


rm -r ../tables_for_views

#? mindbender search drop
# # define which port to use for your own Elasticsearch instance launched internally by mindbender
export ELASTICSEARCH_BASEURL=http://localhost:9${RANDOM:0:3}

#this bulk batchsize could be increased to increase speed. Careful, from 200000, it starts not to work so well.
export ELASTICSEARCH_BULK_BATCHSIZE=30000

if [ $sentences_to_be_re_run]
then   
    mindbender search drop
    mindbender search update 
else
    mindbender search update genepheno_association_views genepheno_causation_views gene_mentions_views pheno_mentions_views
fi

cp db_for_gp.url db.url

#export ES_HEAP_SIZE=10g

#PORT=$RANDOM mindbender search gui
