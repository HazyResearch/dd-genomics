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
          ('section1_id', 'text'),
          ('sent1_id', 'int'),
          ('section2_id', 'text'),
          ('sent2_id', 'int'),
          ('words1', 'text[]'),
          ('lemmas1', 'text[]'),
          ('poses1', 'text[]'),
          ('dep_paths1', 'text[]'),
          ('dep_parents1', 'int[]'),
          ('words2', 'text[]'),
          ('lemmas2', 'text[]'),
          ('poses2', 'text[]'),
          ('dep_paths2', 'text[]'),
          ('dep_parents2', 'int[]'),
          ('gene_mention_ids', 'text[]'),
          ('gene_entities', 'text[]'),
          ('gene_wordidxs', 'int[][]'),
          ('gene_is_corrects', 'boolean[]'),
          ('variant_mention_ids', 'text[]'),
          ('variant_entities', 'text[]'),
          ('variant_wordidxs', 'int[][]'),
          ('variant_is_corrects', 'boolean[]')])


# This defines the output Relation object
Relation = collections.namedtuple('Relation', [
            'dd_id',
            'relation_id',
            'doc_id',
            'section1_id',
            'sent1_id',
            'section2_id',
            'sent2_id',
            'gene_mention_id',
            'gene_entity',
            'gene_wordidxs',
            'gene_is_correct',
            'variant_mention_id',
            'variant_entity',
            'variant_wordidxs',
            'variant_is_correct',
            'is_correct',
            'relation_supertype',
            'relation_subtype'])

### CANDIDATE EXTRACTION ###

def extract_candidate_relations(row):
  # HF = config.GENE_VARIANT['HF']

  relations = []
  # dep_dag = deps.DepPathDAG(row.dep_parents, row.dep_paths, row.words, max_path_len=HF['max-dep-path-dist'])
  for i,gid in enumerate(row.gene_mention_ids):
    for j,pid in enumerate(row.variant_mention_ids):
      r = create_relation(row, i, j)
      relations.append(r)
  return relations


def create_relation(row, i, j):
  gene_mention_id = row.gene_mention_ids[i]
  gene_entity = row.gene_entities[i]
  gene_wordidxs = row.gene_wordidxs[i]
  gene_is_correct = row.gene_is_corrects[i]
  variant_mention_id = row.variant_mention_ids[j]
  variant_entity = row.variant_entities[j]
  variant_wordidxs = row.variant_wordidxs[j]
  variant_is_correct = row.variant_is_corrects[j]
  
  # XXX HACK Johannes: Just set every possible variant-gene pair to true for the moment
  is_correct = True
  supertype = 'DEFAULT_EVERYTHING_TRUE'
  subtype = None

  relation_id = '%s_%s' % (gene_mention_id, variant_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.section1_id, \
               row.sent1_id, row.section2_id, row.sent2_id, \
               gene_mention_id, gene_entity, gene_wordidxs, \
               gene_is_correct, variant_mention_id, variant_entity, \
               variant_wordidxs, variant_is_correct, is_correct, supertype, subtype)
  return r

if __name__ == '__main__':
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    
    # find candidate mentions
    relations = extract_candidate_relations(row)

    # print output
    for relation in relations:
      util.print_tsv_output(relation)
