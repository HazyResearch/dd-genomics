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
          ('gene_mention_ids', 'text[]'),
          ('gene_entities', 'text[]'),
          ('gene_wordidxs', 'int[][]'),
          ('gene_is_corrects', 'boolean[]'),
          ('pheno_mention_ids', 'text[]'),
          ('pheno_entities', 'text[]'),
          ('pheno_wordidxs', 'int[][]'),
          ('pheno_is_corrects', 'boolean[]')])


# This defines the output Relation object
Relation = collections.namedtuple('Relation', [
            'dd_id',
            'relation_id',
            'doc_id',
            'section_id',
            'sent_id',
            'gene_mention_id',
            'gene_entity',
            'gene_wordidxs',
            'gene_is_correct',
            'pheno_mention_id',
            'pheno_entity',
            'pheno_wordidxs',
            'pheno_is_correct'])

### CANDIDATE EXTRACTION ###

def extract_candidate_relations(row):
  """
  row_id = '%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id)
  util.print_error('%s: GE: %s' % (row_id, row.gene_entities))
  util.print_error('%s: GMIDS: %s' % (row_id, row.gene_mention_ids))
  util.print_error('%s: PE: %s' % (row_id, row.pheno_entities))
  util.print_error('%s: PMIDS: %s' % (row_id, row.pheno_mention_ids))
  """

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
  # E.g. the ith pair is row.gene_mention_ids[i], row.pheno_mention_ids[i]
  pairs = []
  for i in range(len(row.gene_mention_ids)):
    rid = '%s_%s' % (row.gene_mention_ids[i], row.pheno_mention_ids[i])
    r = Relation(None, rid, row.doc_id, row.section_id, row.sent_id, \
          row.gene_mention_ids[i], row.gene_entities[i], \
          row.gene_wordidxs[i], row.gene_is_corrects[i], \
          row.pheno_mention_ids[i], row.pheno_entities[i], \
          row.pheno_wordidxs[i], row.pheno_is_corrects[i])

    # Do not consider overlapping mention pairs
    if len(set(r.gene_wordidxs).intersection(r.pheno_wordidxs)) > 0:
      continue

    # Get the min path length between any of the g / p phrase words
    d = dep_dag.path_len_sets(r.gene_wordidxs, r.pheno_wordidxs)
    pairs.append((d, r))

  # Select which of the pairs will be considered
  pairs.sort()
  seen_g = {}
  seen_p = {}
  seen_pairs = {}
  for d, r in pairs:
    if HF.get('take-best-only-dups'):
      e = '%s_%s' % (r.gene_entity, r.pheno_entity)
      if e in seen_pairs and d > seen_pairs[e]:
        continue
      else:
        seen_pairs[e] = d
    
    if HF.get('take-best-only'):
      if (r.gene_mention_id in seen_g and seen_g[r.gene_mention_id] < d) \
        or (r.pheno_mention_id in seen_p and seen_p[r.pheno_mention_id] < d):
        continue

    seen_g[r.gene_mention_id] = d
    seen_p[r.pheno_mention_id] = d
    relations.append(r)
  return relations

if __name__ == '__main__':
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    
    # find candidate mentions
    relations = extract_candidate_relations(row)

    # print output
    for relation in relations:
      util.print_tsv_output(relation)
