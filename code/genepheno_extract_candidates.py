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

Row = collections.namedtuple('Row', [
    'doc_id', 'sent_id', 'gene_mention_id', 'gene_entity', 'gene_wordidxs',
    'pheno_mention_id', 'pheno_entity', 'pheno_wordidxs'])

def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/hpo_phenotype_genes.tsv' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_symbol = line.strip().split('\t')
      supervision_pairs.add((hpo_id, gene_symbol))
  return supervision_pairs

def parse_input_row(line):
  tokens = line.strip().split('\t')
  return Row(*tokens)

def create_mention_for_row(row):
  relation_id = '%s_%s' % (row.gene_mention_id, row.pheno_mention_id)
  entity_pair = (row.pheno_entity, row.gene_entity)
  is_correct = None
  if entity_pair in CACHE['supervision_data']:
    is_correct = True
  elif random.random() < NEGATIVE_EXAMPLE_PROB:
    # Randomly choose some examples to supervise as negatives
    is_correct = False
  return (None, relation_id, row.doc_id, row.sent_id, row.gene_mention_id, \
          row.gene_entity, row.gene_wordidxs, row.pheno_mention_id, row.pheno_entity, \
          row.pheno_wordidxs, is_correct)

if __name__ == '__main__':
  CACHE['supervision_data'] = read_supervision()
  util.run_main_tsv(row_parser=parse_input_row, row_fn=lambda row : [create_mention_for_row(row)])
