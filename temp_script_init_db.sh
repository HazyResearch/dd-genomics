#! /bin/bash

#This is to be included in the run.sh finally when we run with ddlog, used now locally and to test rapidely

if [ -f env_local.sh ]; then
  echo "Using env_local.sh"
  source ./env_local.sh
else
  echo "Using env.sh"
  source ./env.sh
fi

deepdive initdb

#cd parser
#./load_sentences.sh ../../genomics_sentences_10k.tsv sentences

deepdive sql < ../sentences_10k_from_production.sql

deepdive sql """ DROP TABLE IF EXISTS sentences_input CASCADE;
            ALTER TABLE sentences_input_10k_temp RENAME TO sentences_input;"""


# cd ..
./hack_pipelines.py

#this doesn't have to be included in the run.sh finally (since serialize will be in the pipeline of ddlog) but useful here to make it work with application.conf locally

# deepdive sql  """
#         DROP TABLE IF EXISTS sentences_input CASCADE;
#         CREATE TABLE 
#           sentences_input
#         AS (SELECT
#           doc_id,
#           section_id,
#           sent_id,
#           array_to_string(words, '|^|') AS words,
#           array_to_string(lemmas, '|^|') AS lemmas,
#           array_to_string(poses, '|^|') AS poses,
#           array_to_string(ners, '|^|') AS ners,
#           array_to_string(dep_paths, '|^|') AS dep_paths,
#           array_to_string(dep_parents, '|^|') AS dep_parents
#         FROM
#           sentences) """