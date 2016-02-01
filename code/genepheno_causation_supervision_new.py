#! /usr/bin/env python
import random
import re
import sys
from collections import namedtuple
from extractor_util import RowParser, run_main_tsv, APP_HOME
from data_util import read_hpo_dag
from treedlib import corenlp_to_xmltree, Mention, Between, Filter, Children, Ngrams

# This defines the Row object that we read in to the extractor
parser = RowParser([
            ('relation_id', 'text'),
            ('doc_id', 'text'),
            ('section_id', 'text'),
            ('sent_id', 'int'),
            ('gene_mention_id', 'text'),
            ('gene_name', 'text'),
            ('gene_wordidxs', 'int[]'),
            ('gene_is_correct', 'boolean'),
            ('pheno_mention_id', 'text'),
            ('pheno_entity', 'text'),
            ('pheno_wordidxs', 'int[]'),
            ('pheno_is_correct', 'boolean'),
            ('words', 'text[]'),
            ('lemmas', 'text[]'),
            ('poses', 'text[]'),
            ('dep_paths', 'text[]'),
            ('dep_parents', 'int[]')])

# This defines the output Relation object
Relation = namedtuple('Relation', 'dd_id,relation_id,doc_id,section_id,sent_id,gene_mention_id,gene_name,gene_wordidxs,pheno_mention_id,pheno_entity,pheno_wordidxs,is_correct,relation_supertype,relation_subtype')

# This is for XMLTree production
# NOTE the switch from dep_paths -> dep_labels!
CoreNLPSentence = namedtuple('CoreNLPSentence', 'words, lemmas, poses, dep_labels, dep_parents')


# TODO: Do all this as preprocessing!!
HPO_DAG = read_hpo_dag()

def read_charite_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/canon_phenotype_to_gene.map' % APP_HOME) as f:
    for line in f:
      hpo_id, gene_name = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      for h in hpo_ids:
        supervision_pairs.add((h, gene_name))
  return supervision_pairs

CHARITE_PAIRS = read_charite_supervision()


def tag_seq(words, seq, tag):
  """Sub in a tag for a subsequence of a list"""
  words_out = words[:seq[0]] + ['{{%s}}' % tag]
  words_out += words[seq[-1] + 1:] if seq[-1] < len(words) - 1 else []
  return words_out


def apply_rules(rules, f, label, default_weight=0):
  """
  Takes as input a list of rules which are each either a pattern or a (pattern, weight) tuple/list
  Applies f to the pattern
  If true, yields a (label, weight) pair, subbing in the deault weight if necessary
  """
  for rule in rules:
    if type(rule) == list or type(rule) == tuple:
      p, w = rule
    else:
      p = rule
      w = default_weight
    if f(p):
      yield [label, w]

def apply_rgx_rules(rules, string, label, default_weight=0, flags=re.I):
  f = lambda p : re.search(p, string, flags=flags) is not None
  return apply_rules(rules, f, label, default_weight=default_weight)


def get_labels(r, root):
  """Gather the labels produced by each applicable rule, along with the rule weights"""
  labels = []
  cids = [r.gene_wordidxs, r.pheno_wordidxs]
  seq = ' '.join(tag_seq(tag_seq(r.words, r.gene_wordidxs, 'G'), r.pheno_wordidxs, 'P'))
  
  # RULE over sequence + charite
  # Label T if (a) in charite pairs and (b) matches regex
  # W = 1.0
  RGX = r'(mutat|delet|duplicat|truncat|SNP).*caus'
  if (r.pheno_entity, r.gene_name) in CHARITE_PAIRS and re.search(RGX, seq, flags=re.I):
    labels.append(['CHARITE_SUP_WORDS', 1.0])
  
  # RULE over sequence
  # Label T / F if *any part* of full sentence matches regex
  # DEFAULT W = 0.15
  pos = [
    r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*(implicated?|found).*{{P}}',
    r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*cause.*{{P}}', 
    r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*described.*patients.*{{P}}',
    r'.*patient.*{{G}}.*present with.*clinical.*{{P}}.*',
    r'(single nucleotide polymorphisms|SNPs) in {{G}}.*cause.*{{P}}',
    r'(mutation|deletion).*{{G}}.*described.*patients.*{{P}}',
    'role',
    'detected',
    ('{{P}}.*(are|is) (due to|caused by|result of).*{{G}}', 0.7)
  ]
  for label in apply_rgx_rules(pos, seq, 'POS_RGX', default_weight=0.15):
    labels.append(label)

  neg = [
    (r'{{P}}.*not cause.*{{G}}', -0.9),
    (r'{{G}}.*not cause.*{{P}}', -0.9),
    r'\?\s*$',
    r'^\s*To determine', 
    r'^\s*To evaluate', 
    r'^\s*To investigate',
    r'^\s*We investigated',
    '\d+ h ', 
    r'^\s*To assess', 
    r'^\s*here we define', 
    r'^\s*whether',
    'unlikely.*{{G}}.*{{P}}',
    ('{{P}}.*not (due to|caused by).*{{G}}', -0.9),
    ('{{G}}.*not.*cause of.*{{P}}', -0.9),
    '{{G}}.*linked to.*{{P}}',
    'possible association',
    'to investigate', 
    'could reveal', 
    'to determine',
    'could not determine',
    'unclear', 
    'hypothesize', 
    'to evaluate', 
    'plasma', 
    'expression', 
    'to detect',
    ('mouse', -0.8),
    ('mice', -0.8),
    'to find out', 
    'inconclusive', 
    'further analysis',
    'but not',
    'deficiency',
    'activity',
    'variance', 
    'gwas', 
    'association study',
    'possible association', 
    'association'
    'associated with',
    ('conflicting results', -0.8)
  ]
  for label in apply_rgx_rules(neg, seq, 'NEG_RGX', default_weight=-0.15):
    labels.append(label)
  
  # RULE over dep-tree
  # Label T / F based on path between
  btwn = Ngrams(Between(Mention(0), Mention(1)), 'lemma', 1).result_set(root, cids)
  pos = [
    ('role', 0.3),
    'detected'
  ]
  for label in apply_rules(pos, lambda p : p in btwn, 'POS_PATH_BTWN', 0.5):
    labels.append(label)
  
  neg = [
    'unlikely'
  ]
  for label in apply_rules(neg, lambda p : p in btwn, 'NEG_PATH_BTWN', -0.5):
    labels.append(label)

  # RULE over dep-tree
  # Label T / F based on matches of modifiers of VBs on the shortest path between
  vb1_mods = Ngrams(Children(Filter(Between(Mention(0), Mention(1)), 'pos', 'VB')), 'dep_label', 1).result_set(root, cids)
  neg = ['neg']
  for label in apply_rules(neg, lambda p : p in vb1_mods, 'NEG_VB1_MOD', -0.8):
    labels.append(label)

  # RULE over dep-tree
  # Label T / F based on VBs on shortest path between
  #vbs = Ngrams(Filter(Between(Mention(0), Mention(1)), 'pos', 'VB'), 'lemma', 1).result_set(root, cids)
  # TODO

  # RULE over dep-tree
  # Label T / F if word matches a node within distance D of G / P
  # DEFAULT W = 0.4, D = 2
  # TODO

  return labels


def get_final_label(labels):
  """
  Given a set of labels, which is a list of (description, score) duples
  Label TRUE (FALSE) w.p. 1 if SUM(scores) >= 1.0 (<= -1.0)
  Else, label TRUE / FALSE w.p. SUM(scores)
  """
  if len(labels) == 0:
    return None, None
  descriptions, scores = zip(*labels)
  slug = '|'.join(descriptions)
  score = sum(scores)
  if score >= 1.0:
    return True, slug
  elif score <= -1.0:
    return False, slug
  elif random.random() < abs(score):
    return (score > 0), slug
  else:
    return None, None


def supervise(r):
  """Given an input row, return a supervised relation object"""
  # If G or P is false, exclude as a candidate
  if r.gene_is_correct != False and r.pheno_is_correct != False:

    # Get XML tree here
    # TODO: Move to preprocessing
    s = CoreNLPSentence(r.words, r.lemmas, r.poses, r.dep_paths, r.dep_parents)
    xt = corenlp_to_xmltree(s)

    # Perform supervision
    is_correct, supertype = get_final_label(get_labels(r, xt.root))
    yield Relation(None, r.relation_id, r.doc_id, r.section_id, r.sent_id, r.gene_mention_id, r.gene_name, r.gene_wordidxs, r.pheno_mention_id, r.pheno_entity, r.pheno_wordidxs, is_correct, supertype, None)


# Run extractor
run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=supervise)
