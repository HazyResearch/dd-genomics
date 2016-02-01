#! /bin/bash

deepdive sql """
COPY (
select distinct pheno_entity, ensembl_id from genepheno_causation c join genepheno_causation_inference_label_inference i on (c.relation_id = i.relation_id) join genes g on (g.gene_name = c.gene_name) where expectation > 0.9) TO STDOUT
"""
