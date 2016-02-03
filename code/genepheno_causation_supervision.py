#! /usr/bin/env python
import random
import re
import sys
from collections import namedtuple
from extractor_util import RowParser, run_main_tsv, APP_HOME
from data_util import read_hpo_dag
from treedlib import corenlp_to_xmltree, Compile, Ngrams, Mention, Between, Filter, Children, Parents, LeftSiblings, RightSiblings

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


def apply_rules(labels, rule_triple, f):
  """
  Takes as input a triple containing (rule_label, defaul_weight, rules)
  Where rules is a list of rules which are each either a pattern or a (pattern, weight) tuple/list
  Applies f to the pattern
  If true, appends a (label, weight) pair to labels, using the deault weight if necessary
  """
  label, w, rules = rule_triple
  for rule in rules:
    if type(rule) == list or type(rule) == tuple:
      p, w = rule
    else:
      p = rule
    if f(p):
      labels.append([label, w])

def apply_rgx_rules(labels, rule_triple, string, flags=re.I):
  apply_rules(labels, rule_triple, lambda p : re.search(p, string, flags=flags) is not None)

def apply_set_rules(labels, rule_triple, word_set):
  apply_rules(labels, rule_triple, lambda x : x in word_set)

CHARITE_SUP_RGX = (
  'CHARITE_SUP_RGX',  # Rule supertype label
  1.0,                # Rule default weight
  [
    r'(mutat|delet|duplicat|truncat|SNP).*caus'
  ])

POS_RGX = (
  'POS_RGX',
  0.5,
  [
    r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*(implicated?|found).*{{P}}',
    r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*cause.*{{P}}', 
    r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*described.*(patient|family).*{{P}}',
    r'.*patient.*{{G}}.*present with.*clinical.*{{P}}.*',
    r'(single nucleotide polymorphisms|SNPs) in {{G}}.*cause.*{{P}}',
    r'(mutation|deletion).*{{G}}.*described.*patients.*{{P}}',
    ('{{P}}.*(are|is) (attributable to|due to|caused by|result of).*{{G}}', 0.7),
    r'known {{G}} mutation',
    r'{{G}}.*responsible for.*{{P}}',
    r'homozygous for {{G}} mutation.*{{P}}',
    r'{{G}}\s*-\s*related {{P}}',
    r'{{G}} symptoms (include|are|consist of).*{{P}}',
    r'{{P}} results from.*{{G}}'
  ])

NEG_RGX = (
  'NEG_RGX',
  -0.5,
  [
    (r'{{P}}.*not cause.*{{G}}', -0.9),
    (r'{{G}}.*not cause.*{{P}}', -0.9),
    r'\?\s*$',
    (r'^\s*To (establish|determine|evaluate|investigate|analyze|study|asses)', -0.8),
    (r'to (establish|detect|determine|evaluate|investigate|analyze|study|asses)', -0.4),
    (r'^\s*We (evaluated|investigated|analyzed|studied)', -0.4),
    (r'^(Although|However)', -0.2),
    '\d+ h ', 
    r'^\s*here we define', 
    r'^\s*whether',
    'unlikely.*{{G}}.*{{P}}',
    ('{{P}}.*not (due to|caused by).*{{G}}', -0.9),
    ('{{G}}.*not.*cause of.*{{P}}', -0.9),
    '{{G}}.*linked to.*{{P}}',
    'possible association',
    'could reveal', 
    'could not determine',
    ('unclear|unknown', -0.5),
    'hypothesize', 
    'plasma', 
    'expression',
    'needs',
    'our aim',
    ('mouse', -0.8),
    ('mice', -0.8),
    'to find out', 
    'inconclusive', 
    'further (analysis|stud.*)',
    'but not',
    'deficiency',
    'activity',
    'variance', 
    'gwas',
    ('suggests|possible', -0.2),
    'association study',
    ('association', -0.5),
    'associated with',
    ('potential role', -0.5),
    ('conflicting results', -0.8),
  ])

POS_PATH_BTWN = (
  'POS_PATH_BTWN',
  0.7,
  [
    'responsible',
    'attributable',
    'had',
    'include'
  ])

NEG_PATH_BTWN = (
  'NEG_PATH_BTWN',
  -0.7,
  [
    'unlikely',
    'suggest',
    'possible',
    'role',
    'associate',
    'unknown',
    'potential'
  ])

NEG_VB_MOD = (
  'NEG_VB_MOD',
  -0.8,
  [
    'neg'
  ])

NEG_G_DEP_NB = (
  'NEG_G_DEP_NB',
  -0.8,
  [
   'express', 
   'expression', 
   'coexpression', 
   'coexpress', 
   'co-expression',
   'co-express', 
   'overexpress', 
   'overexpression', 
   'over-expression',
   'over-express', 
   'somatic', 
   'infection', 
   'interacts', 
   'regulate',
   'up-regulate', 
   'upregulate', 
   'down-regulate', 
   'downregulate', 
   'production',
   'product', 
   'increased', 
   'increase', 
   'increas',
   'deficiency'
  ])

POS_G_DEP_NB = (
  'POS_G_DEP_NB',
  0.8,
  [
    'known'
  ])

NEG_P_DEP_NB = (
  'NEG_P_DEP_NB',
  -0.8,
  [
    'without',
    'except'
  ])

POS_P_DEP_NB = (
  'POS_P_DEP_NB',
  0.8,
  [])

def get_labels(r, root):
  """Gather the labels produced by each applicable rule, along with the rule weights"""
  labels = []
  cids = [r.gene_wordidxs, r.pheno_wordidxs]
  seq = ' '.join(tag_seq(tag_seq(r.words, r.gene_wordidxs, 'G'), r.pheno_wordidxs, 'P'))
  
  # RULE over sequence + charite: Label T if (a) in charite pairs and (b) matches regex
  if (r.pheno_entity, r.gene_name) in CHARITE_PAIRS:
    apply_rgx_rules(labels, CHARITE_SUP_RGX, seq)
  
  # RULE over sequence: Label if *any part* of full sentence matches regex
  apply_rgx_rules(labels, POS_RGX, seq)
  apply_rgx_rules(labels, NEG_RGX, seq)
  
  # RULE over dep-tree: Label based on path between
  btwn = Ngrams(Between(Mention(0), Mention(1)), 'lemma', 1).result_set(root, cids)
  apply_set_rules(labels, POS_PATH_BTWN, btwn)
  apply_set_rules(labels, NEG_PATH_BTWN, btwn)

  # RULE over dep-tree: Label based on matches of modifiers of VBs on the shortest path between
  vb_mods = Ngrams(Children(Filter(Between(Mention(0), Mention(1)), 'pos', 'VB')), 'dep_label', 1).result_set(root, cids)
  apply_set_rules(labels, NEG_VB_MOD, vb_mods)

  # RULE over dep-tree:Label if word matches a node within distance D of G / P
  neighbors = Compile([
    Ngrams(LeftSiblings(Mention(0)), 'lemma', 1),
    Ngrams(RightSiblings(Mention(0)), 'lemma', 1),
    Ngrams(Parents(Mention(0), 1), 'lemma', 1),
    Ngrams(Children(Mention(0)), 'lemma', 1)
  ])
  g_nbs = neighbors.result_set(root, [r.gene_wordidxs])
  apply_set_rules(labels, NEG_G_DEP_NB, g_nbs)
  apply_set_rules(labels, POS_G_DEP_NB, g_nbs)

  p_nbs = neighbors.result_set(root, [r.pheno_wordidxs])
  apply_set_rules(labels, NEG_P_DEP_NB, p_nbs)
  apply_set_rules(labels, POS_P_DEP_NB, p_nbs)
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
