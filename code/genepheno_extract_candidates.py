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
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('gene_mention_ids', 'text[]'),
          ('gene_entities', 'text[]'),
          ('gene_mention_types', 'text[]'),
          ('gene_wordidxs', 'int[][]'),
          ('gene_is_corrects', 'boolean[]'),
          ('pheno_mention_ids', 'text[]'),
          ('pheno_entities', 'text[]'),
          ('pheno_mention_types', 'text[]'),
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

EID_MAP = dutil.gene_symbol_to_ensembl_id_map()
HPO_DAG = dutil.read_hpo_dag()

def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/canon_phenotype_to_gene.map' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_symbol = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      eids = EID_MAP[gene_symbol]
      for h in hpo_ids:
        for e in eids:
          supervision_pairs.add((h,e))
  return supervision_pairs


### CANDIDATE EXTRACTION ###

def extract_candidate_relations(row, superv_diff=0):
  """
  Given a row object having a sentence and some associated N gene and M phenotype mention
  candidates, pick a subset of the N*M possible gene-phenotype relations to return as
  candidate relations
  Optionally pass in the current difference between pos & neg supervision counts
  And use for supervision
  """
  HF = config.GENE_PHENO['HF']
  SR = config.GENE_PHENO['SR']

  relations = []

  # Create a dependencies DAG for the sentence
  dep_dag = deps.DepPathDAG(row.dep_parents, row.dep_paths, row.words, max_path_len=HF['max-dep-path-dist'])

  # Create the list of possible G,P pairs with their dependency path distances
  pairs = []
  for i,gid in enumerate(row.gene_mention_ids):
    for j,pid in enumerate(row.pheno_mention_ids):

      # Do not consider overlapping mention pairs
      if len(set(row.gene_wordidxs[i]).intersection(row.pheno_wordidxs[j])) > 0:
        continue

      # Get the min path length between any of the g / p phrase words
      l = dep_dag.path_len_sets(row.gene_wordidxs[i], row.pheno_wordidxs[j])
      if l:
        pairs.append([l, i, j])
      elif SR.get('bad-dep-paths'):
        relations.append(create_supervised_relation_simple(row, i, j, relation_type='BAD_OR_NO_DEP_PATH'))

  # Select which of the pairs will be considered
  pairs.sort()
  seen_g = {}
  seen_p = {}
  seen_pairs = {}
  for p in pairs:
    d, i, j = p

    # If the same entity occurs several times in a sentence, only take best one
    if HF.get('take-best-only-dups'):
      e = '%s_%s' % (row.gene_entities[i], row.pheno_entities[j])
      if e in seen_pairs and d > seen_pairs[e]:
        continue
      else:
        seen_pairs[e] = d
    
    # HACK[Alex]: may or may not be hack, needs to be tested- for now be quite restrictive
    # Only take the set of best pairs which still provides coverage of all entities
    if HF.get('take-best-only'):
      if (i in seen_g and seen_g[i] < d) or (j in seen_p and seen_p[j] < d):
        continue

    seen_g[i] = d
    seen_p[j] = d
    r = create_supervised_relation(row, i, j, superv_diff, dep_dag)
    if r is not None:
      relations.append(r)
  return relations


def create_supervised_relation(row, i, j, superv_diff, dep_dag=None):
  """
  Given a Row object with a sentence and several gene and pheno objects, create and 
  supervise a Relation output object for the ith gene and jth pheno objects
  Note: outputs a list for convenience
  Also includes an input for d = pos - neg supervision count, for neg supervision
  """
  gene_mention_id = row.gene_mention_ids[i]
  gene_entity = row.gene_entities[i]
  gene_mention_type = row.gene_mention_types[i]
  gene_wordidxs = row.gene_wordidxs[i]
  gene_is_correct = row.gene_is_corrects[i]
  pheno_mention_id = row.pheno_mention_ids[j]
  pheno_entity = row.pheno_entities[j]
  pheno_wordidxs = row.pheno_wordidxs[j]
  pheno_is_correct = row.pheno_is_corrects[j]

  phrase = ' '.join(row.words)
  lemma_phrase = ' '.join(row.lemmas)
  b = sorted([gene_wordidxs[0], gene_wordidxs[-1], pheno_wordidxs[0], pheno_wordidxs[-1]])[1:-1]
  between_phrase = ' '.join(row.words[i] for i in range(b[0]+1,b[1]))
  between_phrase_lemmas = ' '.join(row.lemmas[i] for i in range(b[0]+1,b[1]))

  dep_path_between = frozenset(dep_dag.min_path_sets(gene_wordidxs, pheno_wordidxs)) if dep_dag else None

  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.sent_id, gene_mention_id, gene_entity, \
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None)
  
  # distant supervision rules & hyperparameters
  # NOTE: see config.py for all documentation & values
  SR = config.GENE_PHENO['SR']
  VALS = config.GENE_PHENO['vals']

  if SR.get('ignore-noncanonical'):
    if re.search(r'noncanonical', gene_mention_type, flags=re.I):
      return None

  if SR.get('g-or-p-false'):
    opts = SR['g-or-p-false']
    if not (gene_is_correct != False and pheno_is_correct != False):
      if random.random() < opts['diff']*superv_diff or random.random() < opts['rand']:
        return r._replace(is_correct=False, relation_type='G_ANDOR_P_FALSE')
      else:
        return None

  if SR.get('adjacent-false'):
    if re.search(r'[a-z]{3,}', between_phrase, flags=re.I) is None:
      if random.random() < 0.5*superv_diff or random.random() < 0.01:
        return r._replace(is_correct=False, relation_type='G_P_ADJACENT')
      else:
        return None

  if SR.get('phrases-in-sent'):
    opts = SR['phrases-in-sent']
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0 and \
        re.search(util.rgx_comp(opts[name], rgxs=opts['%s-rgx' % name]), phrase + ' ' + lemma_phrase, flags=re.I):
        return r._replace(is_correct=val, relation_type='PHRASE_%s' % name)

  if SR.get('phrases-in-between'):
    opts = SR['phrases-in-between']
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0 and \
        re.search(util.rgx_comp(opts[name], rgxs=opts['%s-rgx' % name]), between_phrase + ' ' + between_phrase_lemmas, flags=re.I):
        return r._replace(is_correct=val, relation_type='PHRASE_BETWEEN_%s' % name)

  if SR.get('primary-verb-modifiers') and dep_dag:
    opts = SR['primary-verb-modifiers']
    if dep_path_between:
      verbs_between = [i for i in dep_path_between if row.poses[i].startswith("VB")]
      if len(verbs_between) > 0:
        for name,val in VALS:
          mod_words = [i for i,x in enumerate(row.lemmas) if x in opts[name]]
          mod_words += [i for i,x in enumerate(row.dep_paths) if x in opts['%s-dep-tag' % name]]
          d = dep_dag.path_len_sets(verbs_between, mod_words)
          if d and d < opts['max-dist'] + 1:
            return r._replace(is_correct=val, relation_type='PRIMARY_VB_MOD_%s' % name) 

  if SR.get('dep-lemma-connectors') and dep_dag:
    opts = SR['dep-lemma-connectors']
    for name,val in VALS:
      if dep_path_between and \
        len([i for i,x in enumerate(row.lemmas) if i in dep_path_between and x in opts[name]]) > 0:
        return r._replace(is_correct=val, relation_type='DEP_LEMMA_CONNECT_%s' % name)

  if SR.get('dep-lemma-neighbors') and dep_dag:
    opts = SR['dep-lemma-neighbors']
    for name,val in VALS:
      for entity in ['g','p']:
        d = dep_dag.path_len_sets(gene_wordidxs, [i for i,x in enumerate(row.lemmas) if x in opts['%s-%s' % (name,entity)]])
        if d and d < opts['max-dist'] + 1:
          return r._replace(is_correct=val, relation_type='DEP_LEMMA_NB_%s_%s' % (name,entity))

  if SR.get('charite-all-pos'):
    if (pheno_entity, gene_entity) in CHARITE_PAIRS:
      return r._replace(is_correct=True, relation_type='CHARITE_SUP') 

  # Return GP relation object
  return r


def create_supervised_relation_simple(row, i, j, is_correct=False, relation_type='TESTING'):
  gene_mention_id = row.gene_mention_ids[i]
  pheno_mention_id = row.pheno_mention_ids[j]
  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  return Relation(None, relation_id, row.doc_id, row.sent_id, gene_mention_id, row.gene_entities[i], \
            row.gene_wordidxs[i], pheno_mention_id, row.pheno_entities[j], row.pheno_wordidxs[j], \
            is_correct, relation_type)


if __name__ == '__main__':

  # load in static data
  CHARITE_PAIRS = read_supervision()

  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  pos_count = 0
  neg_count = 0
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    
    # find candidate mentions & supervise
    relations = extract_candidate_relations(row, superv_diff=pos_count-neg_count)

    pos_count += len(filter(lambda r : r.is_correct, relations))
    neg_count += len(filter(lambda r : r.is_correct is False, relations))

    # print output
    for relation in relations:
      util.print_tsv_output(relation)
