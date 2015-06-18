#!/usr/bin/env python
import collections
import extractor_util as util
import data_util as dutil
import dep_util as deps
import os
import random
import re
import sys

CACHE = dict()  # Cache results of disk I/O


# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('gene_mention_ids', 'text[]'),
          ('gene_entities', 'text[]'),
          ('gene_wordidxs', 'int[][]'),
          ('pheno_mention_ids', 'text[]'),
          ('pheno_entities', 'text[]'),
          ('pheno_wordidxs', 'int[][]')])


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


def gene_symbol_to_ensembl_id_map():
  """Maps a gene symbol from CHARITE -> ensembl ID"""
  with open('%s/onto/data/ensembl_genes.tsv' % util.APP_HOME) as f:
    eid_map = collections.defaultdict(set)
    for line in f:
      eid, phrase, mapping_type = line.rstrip('\n').split('\t')
      eid_map[phrase].add(eid)
      eid_map[phrase.lower()].add(eid)
  return eid_map


EID_MAP = gene_symbol_to_ensembl_id_map()

HPO_DAG = dutil.read_hpo_dag()


def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/hpo_phenotype_genes.tsv' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_symbol = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      eids = EID_MAP[gene_symbol]
      for h in hpo_ids:
        for e in eids:
          supervision_pairs.add((h,e))
  return supervision_pairs


### CANDIDATE EXTRACTION ###

def extract_candidate_relations(row):
  """
  Given a row object having a sentence and some associated N gene and M phenotype mention
  candidates, pick a subset of the N*M possible gene-phenotype relations to return as
  candidate relations
  """
  relations = []
  r = Relation(dd_id=None, relation_id=None, doc_id=row.doc_id, sent_id=row.sent_id, \
               gene_mention_id=None, gene_entity=None, gene_wordidxs=None, \
               pheno_mention_id=None, pheno_entity=None, pheno_wordidxs=None, is_correct=None)

  # Create a dependencies DAG for the sentence
  dep_dag = deps.DepPathDAG(row.dep_paths, row.dep_parents)

  # Create the list of possible G,P pairs with their dependency path distances




NEGATIVE_EXAMPLE_PROB = 0.1
def create_mention_for_row(row):
  relation_id = '%s_%s' % (row.gene_mention_id, row.pheno_mention_id)
  entity_pair = (row.pheno_entity, row.gene_entity)

  # Some patterns to skip:

  # If we see <PHENO> (<GENE>) where starting letters are all the same, skip-
  # This is a pheno abbreivation (which said gene false match named after)
  if row.pheno_wordidxs[-1] + 2 == row.gene_wordidxs[0]:
    pi = row.pheno_wordidxs[-1]
    if row.words[pi+1] == '(':
      slp = ''.join([row.words[wi][0] for wi in row.pheno_wordidxs]).lower()
      if slp == row.words[row.gene_wordidxs[0]].lower():
        return []

  # Handle preprocessing error here- failure to split sentences on citations
  # HACK[Alex]
  if row.gene_wordidxs[0] < row.pheno_wordidxs[0]:
    between_range = range(row.gene_wordidxs[0]+1, row.pheno_wordidxs[0])
  else:
    between_range = range(row.pheno_wordidxs[-1]+1, row.gene_wordidxs[0])
  for wi in between_range:
    if re.search(r'\.\d+(,\d+)', row.words[wi]):
      return []

  is_correct = None
  if entity_pair in CACHE['supervision_data']:
    is_correct = True

  # Randomly choose some examples to supervise as negatives
  elif random.random() < NEGATIVE_EXAMPLE_PROB:
    is_correct = False
  return [Relation(None, relation_id, row.doc_id, row.sent_id, row.gene_mention_id, \
      row.gene_entity, row.gene_wordidxs, row.pheno_mention_id, row.pheno_entity, \
      row.pheno_wordidxs, is_correct)]


if __name__ == '__main__':

  # load in static data
  CACHE['supervision_data'] = read_supervision()

  # read through and process lines in
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    
    # find candidate mentions & supervise
    try:
      relations = create_mentions_for_row(row)
    except IndexError:
      util.print_error("Error with row: %s" % (row,))
      continue

    # print output
    for relation in relations:
      util.print_tsv_output(relation)
