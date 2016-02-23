#! /bin/bash

if [ -z $DDUSER ]
then
  echo "set dduser/source env_local!" >> /dev/stderr
  exit 1
fi

psql -p 6432 -U $DDUSER -h raiders7 -c "COPY (
select distinct
  si.*
from
  sentences_input si
  join (
    select distinct doc_id from 
      ((select distinct doc_id from sentences_input order by random() LIMIT 50000) 
      union (select distinct doc_id from 
        genepheno_causation_labels l 
        join genepheno_pairs p 
          on (l.relation_id = p.gene_mention_id || '_' || p.pheno_mention_id)) 
      union (select distinct doc_id from 
        genepheno_causation_precision_labels l 
        join genepheno_pairs p on (l.relation_id = p.gene_mention_id || '_' || p.pheno_mention_id))
      union (select distinct doc_id from 
        genepheno_multi_precision_labels l 
        join genepheno_pairs p on (l.relation_id = p.gene_mention_id || '_' || p.pheno_mention_id))
      union (select distinct doc_id from 
        genepheno_facts_precision_labels l 
        join genepheno_pairs p on (l.relation_id = p.gene_mention_id || '_' || p.pheno_mention_id))) a) 
      si2 on (si.doc_id = si2.doc_id)
) TO STDOUT" genomics_jbirgmei
