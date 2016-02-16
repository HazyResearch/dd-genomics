#!/usr/bin/env python
import collections
import extractor_util as util
import data_util as dutil
import dep_util as deps
import os
import random
import re
import sys
import config


# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('gene_mention_id', 'text'),
          ('gene_name', 'text'),
          ('gene_wordidxs', 'int[]'),
          ('gene_is_correct', 'boolean'),
          ('pheno_mention_id', 'text'),
          ('pheno_entity', 'text'),
          ('pheno_wordidxs', 'int[]'),
          ('pheno_is_correct', 'boolean')])


# This defines the output Relation object
Relation = collections.namedtuple('Relation', [
            'dd_id',
            'relation_id',
            'doc_id',
            'section_id',
            'sent_id',
            'gene_mention_id',
            'gene_name',
            'gene_wordidxs',
            'gene_is_correct',
            'pheno_mention_id',
            'pheno_entity',
            'pheno_wordidxs',
            'pheno_is_correct'])

### CANDIDATE EXTRACTION ###

def extract_candidate_relations(row):
  """
  Given a row object having a sentence and some associated N gene and M phenotype mention
  candidates, pick a subset of the N*M possible gene-phenotype relations to return as
  candidate relations
  """
  HF = config.GENE_PHENO['HF']

  relations = []

  # Create a dependencies DAG for the sentence
  dep_dag = deps.DepPathDAG(row.dep_parents, row.dep_paths, row.words, max_path_len=HF['max-dep-path-dist'])

  # Go through the G-P pairs in the sentence, which are passed in serialized format
  pairs = []
  rid = '%s_%s' % (row.gene_mention_id, row.pheno_mention_id)
  r = Relation(None, rid, row.doc_id, row.section_id, row.sent_id, \
        row.gene_mention_id, row.gene_name, \
        row.gene_wordidxs, row.gene_is_correct, \
        row.pheno_mention_id, row.pheno_entity, \
        row.pheno_wordidxs, row.pheno_is_correct)

  # Do not consider overlapping mention pairs
  if len(set(r.gene_wordidxs).intersection(r.pheno_wordidxs)) > 0:
    return []

  # Get the min path length between any of the g / p phrase words
  d = dep_dag.path_len_sets(r.gene_wordidxs, r.pheno_wordidxs)
  if d is not None:
    if d > HF['max-dep-path-dist']:
      return []

  return [r]

if __name__ == '__main__':
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    
    # find candidate mentions
    relations = extract_candidate_relations(row)

    # print output
    for relation in relations:
      util.print_tsv_output(relation)
