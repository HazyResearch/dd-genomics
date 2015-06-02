#!/usr/bin/env python
import collections
import extractor_util as util
import data_util as dutil
import os
import random
import re
import sys

CACHE = dict()  # Cache results of disk I/O

NEGATIVE_EXAMPLE_PROB = 0.1

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'int'),
          ('gene_mention_id', 'text'),
          ('gene_entity', 'text'),
          ('gene_wordidxs', 'int[]'),
          ('pheno_mention_id', 'text'),
          ('pheno_entity', 'text'),
          ('pheno_wordidxs', 'int[]')])

# This defines the output Relation object
Relation = collections.namedtuple('Relation', [
            'dd_id',
            'relation_id',
            'doc_id',
            'sent_id',
            'gene_mention_id',
            'gene_entity',
            'gene_wordidxs',
            'pheno_mention_id',
            'pheno_entity',
            'pheno_wordidxs',
            'is_correct'])

def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/hpo_phenotype_genes.tsv' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_symbol = line.strip().split('\t')
      supervision_pairs.add((hpo_id, gene_symbol))
  return supervision_pairs

def create_mention_for_row(row):

  # Skip row if sentence doesn't contain a verb, contains URL, etc.
  if util.skip_row(row):
    return mentions

  relation_id = '%s_%s' % (row.gene_mention_id, row.pheno_mention_id)
  entity_pair = (row.pheno_entity, row.gene_entity)
  is_correct = None
  if entity_pair in CACHE['supervision_data']:
    is_correct = True

  # Randomly choose some examples to supervise as negatives
  elif random.random() < NEGATIVE_EXAMPLE_PROB:
    is_correct = False
  return Relation(None, relation_id, row.doc_id, row.sent_id, row.gene_mention_id, \
      row.gene_entity, row.gene_wordidxs, row.pheno_mention_id, row.pheno_entity, \
      row.pheno_wordidxs, is_correct)

if __name__ == '__main__':
  CACHE['supervision_data'] = read_supervision()
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=lambda row : [create_mention_for_row(row)])
