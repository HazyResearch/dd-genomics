#! /bin/bash

if [ -z ${GDD_HOME} ]
then
  print "set GDD_HOME!"
  exit 1
fi

cutoff=`cat $GDD_HOME/results_log/gp_cutoff`

deepdive sql """
COPY (
select distinct pheno_entity, ensembl_id from genepheno_association c join genepheno_association_inference_label_inference i on (c.relation_id = i.relation_id) join genes g on (g.gene_name = c.gene_name) where expectation > ${cutoff}) TO STDOUT
"""
