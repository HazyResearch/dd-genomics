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
            'sent_id',
            'gene_mention_id',
            'gene_entity',
            'gene_wordidxs',
            'pheno_mention_id',
            'pheno_entity',
            'pheno_wordidxs',
            'is_correct',
            'relation_type'])


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


# TODO: move to util file
def read_manual_list(name):
  """Reads in simple list of words in TSV format"""
  words = []
  with open('%s/onto/manual/%s.tsv' % (util.APP_HOME, name)) as f:
    for line in f:
      words.append(line.strip().lower())
  return frozenset(words)

POS_SUPERVISION_WORDS = read_manual_list('gp_pos_words')
NEG_SUPERVISION_WORDS = read_manual_list('gp_neg_words')


### CANDIDATE EXTRACTION ###

def extract_candidate_relations(row, superv_diff=0):
  """
  Given a row object having a sentence and some associated N gene and M phenotype mention
  candidates, pick a subset of the N*M possible gene-phenotype relations to return as
  candidate relations
  Optionally pass in the current difference between pos & neg supervision counts
  And use for supervision
  """
  relations = []

  # Create a dependencies DAG for the sentence
  dep_dag = deps.DepPathDAG(row.dep_paths, row.dep_parents)

  # Create the list of possible G,P pairs with their dependency path distances
  pairs = []
  for i,gid in enumerate(row.gene_mention_ids):
    for j,pid in enumerate(row.pheno_mention_ids):

      # Do not consider overlapping mention pairs
      if len(set(row.gene_wordidxs[i]).intersection(row.pheno_wordidxs[j])) > 0:
        continue

      # Get the min path length between any of the g / p phrase words
      ds = []
      for ii in row.gene_wordidxs[i]:
        for jj in row.pheno_wordidxs[j]:
          min_path = dep_dag.min_path(ii, jj)
          if min_path:
            ds.append(len(min_path))
      if len(ds) > 0:
        pairs.append([min(ds), i, j])

  # Select which of the pairs will be considered
  HARD_MAX_DEP_PATH_DIST = 7
  pairs.sort()
  pairs = filter(lambda p : p[0] < HARD_MAX_DEP_PATH_DIST, pairs)
  seen_g = {}
  seen_p = {}
  seen_pairs = {}
  for p in pairs:
    d, i, j = p

    # If the same entity occurs several times in a sentence, only take best one
    e = '%s_%s' % (row.gene_entities[i], row.pheno_entities[j])
    if e in seen_pairs and d > seen_pairs[e]:
      continue
    else:
      seen_pairs[e] = d
    
    # HACK[Alex]: may or may not be hack, needs to be tested- for now be quite restrictive
    """
    if (i in seen_g and seen_g[i] < d) or (j in seen_p and seen_p[j] < d):
      continue
    """
    seen_g[i] = d
    seen_p[j] = d
    r = create_supervised_relation(row, i, j, superv_diff)
    if r is not None:
      relations.append(r)
  return relations


def create_supervised_relation(row, i, j, superv_diff):
  """
  Given a Row object with a sentence and several gene and pheno objects, create and 
  supervise a Relation output object for the ith gene and jth pheno objects
  Note: outputs a list for convenience
  Also includes an input for d = pos - neg supervision count, for neg supervision
  """
  gene_mention_id = row.gene_mention_ids[i]
  gene_entity = row.gene_entities[i]
  gene_wordidxs = row.gene_wordidxs[i]
  gene_is_correct = row.gene_is_corrects[i]
  pheno_mention_id = row.pheno_mention_ids[j]
  pheno_entity = row.pheno_entities[j]
  pheno_wordidxs = row.pheno_wordidxs[j]
  pheno_is_correct = row.pheno_is_corrects[j]

  row_words = set([w.lower() for w in row.words + row.lemmas])

  if gene_wordidxs[-1] < pheno_wordidxs[0]:
    between_range = range(gene_wordidxs[-1]+1, pheno_wordidxs[0])
  else:
    between_range = range(pheno_wordidxs[-1]+1, gene_wordidxs[0])
  between_phrase = ' '.join(row.words[i] for i in between_range)

  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.sent_id, gene_mention_id, gene_entity, \
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None)

  # Handle preprocessing error here- failure to split sentences on citations
  # HACK[Alex]
  for wi in between_range:
    if re.search(r'\.\d+(,\d+)', row.words[wi]):
      return r._replace(is_correct=False, relation_type='SPLIT_SENTENCE')

  # label adjacent mentions as false
  if re.search(r'[a-z]{3,}', between_phrase, flags=re.I) is None:
    if random.random() < 0.5*superv_diff or random.random() < 0.01:
      return r._replace(is_correct=False, relation_type='G_P_ADJACENT')
    else:
      return None

  # label any example where either the gene, pheno or both is false as neg example
  if not (gene_is_correct != False and pheno_is_correct != False):
    if random.random() < 0.5*superv_diff or random.random() < 0.01:
      return r._replace(is_correct=False, relation_type='G_ANDOR_P_FALSE')
    else:
      return None

  # neg supervision word
  # TODO: handle n-grams too
  if len(row_words.intersection(NEG_SUPERVISION_WORDS)) > 0:
    if (pheno_entity, gene_entity) in CACHE['supervision_data']:
      return r._replace(is_correct=False, relation_type='CHARITE_SUP_NEG_WORDS')
    else:
      return r._replace(is_correct=False, relation_type='NEG_WORDS')

  # positive supervision via Charite
  # TODO: take dep paths into account here too?  E.g. if pos word on a dep path between the G,P?
  if (pheno_entity, gene_entity) in CACHE['supervision_data']:
    if len(row_words.intersection(POS_SUPERVISION_WORDS)) > 0:
      return r._replace(is_correct=True, relation_type='CHARITE_SUP_POS_WORDS')
    else:
      is_correct = True if random.random() < 0.1 else None
      return r._replace(is_correct=is_correct, relation_type='CHARITE_SUP')

  # label any relations where a positive word occurs *between* the G and P as correct
  # TODO: do this for dep paths too!
  if len(POS_SUPERVISION_WORDS.intersection(row.words[i] for i in between_range)) > 0:
    return r._replace(is_correct=True, relation_type='POS_WORD_BETWEEN')

  # Return GP relation object
  return r


if __name__ == '__main__':

  # load in static data
  CACHE['supervision_data'] = read_supervision()

  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  pos_count = 0
  neg_count = 0
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    
    # find candidate mentions & supervise
    relations = extract_candidate_relations(row, superv_diff=pos_count-neg_count)
    """
    try:
      relations = extract_candidate_relations(row, superv_diff=pos_count-neg_count)
    except IndexError:
      util.print_error("Error with row: %s" % (row,))
      continue
    """

    pos_count += len(filter(lambda r : r.is_correct, relations))
    neg_count += len(filter(lambda r : r.is_correct is False, relations))

    # print output
    for relation in relations:
      util.print_tsv_output(relation)
