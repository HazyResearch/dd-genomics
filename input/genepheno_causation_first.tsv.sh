#! /bin/bash -e

deepdive sql """
COPY (
select
  id,
  doc_id,
  section_id,
  sent_id,
  gene_mention_id,
  gene_name,
  gene_wordidxs[1],
  pheno_mention_id,
  pheno_entity,
  pheno_wordidxs[1],
  is_correct,
  supertype,
  subtype
from
  genepheno_causation
) TO STDOUT
"""
