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
      min_path = dep_dag.min_path_phrases(row.gene_wordidxs[i], row.pheno_wordidxs[j])
      if min_path:
        pairs.append([len(min_path), i, j])

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

  # HACK[Alex]: IGNORE ALL NONCANONICAL HERE!!!
  if re.search(r'noncanonical', gene_mention_type, flags=re.I):
    return None

  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.sent_id, gene_mention_id, gene_entity, \
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None)

  ## DS RULE: label any example where either the gene, pheno or both is false as neg example
  if not (gene_is_correct != False and pheno_is_correct != False):
    if random.random() < 0.5*superv_diff or random.random() < 0.01:
      return r._replace(is_correct=False, relation_type='G_ANDOR_P_FALSE')
    else:
      return None

  # Get the set of row words, between words
  row_words = set([w.lower() for w in row.words + row.lemmas])
  gene = row.words[gene_wordidxs[0]]
  pheno = ' '.join(row.words[i] for i in pheno_wordidxs)
  if gene_wordidxs[-1] < pheno_wordidxs[0]:
    between_range = range(gene_wordidxs[-1]+1, pheno_wordidxs[0])
  else:
    between_range = range(pheno_wordidxs[-1]+1, gene_wordidxs[0])
  between_phrase = ' '.join(row.words[i] for i in between_range).lower()
  between_phrase_lemma = ' '.join(row.lemmas[i] for i in between_range).lower()
  whole_phrase = ' '.join(row.words).lower()
  whole_phrase_lemma = ' '.join(row.lemmas).lower()

  # Get intersection with some pos / neg patterns
  # TODO: clean all this up!!
  POS_WORDS = ['mutation', 'mutate', 'cause', 'implicate']
  NEG_WORDS = ['expression', 'express', 'coexpression', 'coexpress', 'co-expression', 'co-express', 'correlate', 'risk-factor', 'risk factor', 'snp', 'single nucleotide polymorphism', 'gwas', 'genome wide association study', 'genome-wide association study', 'found an association']
  POS_RGXS = []
  NEG_RGXS = [r'rs\d+', r'population((\-|\s+)based)?\s+study', r'potential\s+(therapeutic\s+)?target']
  POS_RGX = util.concat_rgx(strings=POS_WORDS, rgxs=POS_RGXS)
  NEG_RGX = util.concat_rgx(strings=NEG_WORDS, rgxs=NEG_RGXS)

  # get indices of matches in sentence
  """
  pos_match_idx = []
  for m in re.finditer(POS_RGX, whole_phrase):
    pos_match_idx += range(m.start(), m.end())
  """

  POS_PATTERNS = [r'{{G}},?\s(a\s{{P}}\sgene|a\sgene\sfor\s{{P}})', r'{{P}}\sgene,?\s{{G}}']
  NEG_PATTERNS = [r'{{G}}\s+level', r'{{P}}\scauses?\s{{G}}']
  POS_PATTERNS, NEG_PATTERNS = [[re.sub(r'{{G}}', re.escape(gene), re.sub(r'{{P}}', re.escape(pheno), p)) for p in ps] for ps in [POS_PATTERNS, NEG_PATTERNS]]
  POS_RGX_P = util.concat_rgx(rgxs=POS_PATTERNS)
  NEG_RGX_P = util.concat_rgx(rgxs=NEG_PATTERNS)

  # TODO: CLEAN ALL THIS UP!!!

  # word between
  # TODO: *or* on dep path!
  pos_a = False
  neg_a = False
  if re.search(POS_RGX, between_phrase) or re.search(POS_RGX, between_phrase_lemma):
    pos_a = True
  if re.search(NEG_RGX, between_phrase) or re.search(NEG_RGX, between_phrase_lemma):
    neg_a = True

  # word match
  pos_b = False
  neg_b = False
  if pos_a or re.search(POS_RGX, whole_phrase) or re.search(POS_RGX, whole_phrase_lemma):
    pos_b = True
  if neg_a or re.search(NEG_RGX, whole_phrase) or re.search(NEG_RGX, whole_phrase_lemma):
    neg_b = True

  # GP PATTERN MATCH
  pos_c = False
  neg_c = False
  if re.search(POS_RGX_P, whole_phrase) or re.search(POS_RGX_P, whole_phrase_lemma):
    pos_c = True
  if re.search(NEG_RGX_P, whole_phrase) or re.search(NEG_RGX_P, whole_phrase_lemma):
    neg_c = True

  ## DS RULE: label adjacent mentions as false
  if re.search(r'[a-z]{3,}', between_phrase, flags=re.I) is None:
    if random.random() < 0.5*superv_diff or random.random() < 0.01:
      return r._replace(is_correct=False, relation_type='G_P_ADJACENT')
    else:
      return None

  ## DS RULE: positive supervision via Charite
  if (pheno_entity, gene_entity) in CACHE['supervision_data']:
    #if len(row_words.intersection(POS_SUPERVISION_WORDS)) > 0:
    if pos_b or pos_c:
      return r._replace(is_correct=True, relation_type='CHARITE_SUP_POS_WORDS')
    else:
      #is_correct = True if random.random() < 0.1 else None
      is_correct=True
      return r._replace(is_correct=is_correct, relation_type='CHARITE_SUP')

  ## DS RULE: neg supervision word
  #if len(row_words.intersection(NEG_SUPERVISION_WORDS)) > 0:
  if neg_b or neg_c:
    if (pheno_entity, gene_entity) in CACHE['supervision_data']:
      return r._replace(is_correct=False, relation_type='CHARITE_SUP_NEG_WORDS')
    else:
      return r._replace(is_correct=False, relation_type='NEG_WORDS')

  ## DS RULE: label any relations where a positive word occurs *between* the G and P as correct
  #if len(POS_SUPERVISION_WORDS.intersection(row.words[i] for i in between_range)) > 0:
  if pos_a or pos_c:
    return r._replace(is_correct=True, relation_type='POS_WORD_BETWEEN')

  # Return GP relation object
  return r


if __name__ == '__main__':

  # load in static data
  CACHE['supervision_data'] = read_supervision()
  """
  POS_SUPERVISION_WORDS = dutil.read_manual_list('gp_pos_words')
  NEG_SUPERVISION_WORDS = dutil.read_manual_list('gp_neg_words')
  """

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
