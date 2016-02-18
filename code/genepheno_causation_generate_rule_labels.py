#! /usr/bin/env python
import random
import re
import sys
from collections import namedtuple
from extractor_util import RowParser, run_main_tsv, APP_HOME
from data_util import read_hpo_dag
from treedlib import corenlp_to_xmltree, Compile, Ngrams, Mention, Between, Filter, Children, Parents, LeftSiblings, RightSiblings
import numpy as np
from itertools import chain

#TODO: Change distributed by so includes doc_id?

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

# Output a rule relation
Label = namedtuple('Label', 'relation_id, rule_id, rule_verbose, heuristic_priority, heuristic_priority_2, label')

# This is for XMLTree production
# NOTE the switch from dep_paths -> dep_labels!
CoreNLPSentence = namedtuple('CoreNLPSentence', 'words, lemmas, poses, dep_labels, dep_parents')


# TODO: Do all this as preprocessing!!
def read_charite_supervision(hpo_dag):
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/canon_phenotype_to_gene.map' % APP_HOME) as f:
    for line in f:
      hpo_id, gene_name = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in hpo_dag.edges[hpo_id]]
      for h in hpo_ids:
        supervision_pairs.add((h, gene_name))
  return supervision_pairs


def tag_seq(words, seq, tag):
  """Sub in a tag for a subsequence of a list"""
  words_out = words[:seq[0]] + ['{{%s}}' % tag]
  words_out += words[seq[-1] + 1:] if seq[-1] < len(words) - 1 else []
  return words_out

def tag_seqs(words, seqs, tags):
  """
  Given a list of words, a *list* of lists of indexes, anmd the corresponding tags
  This function substitutes the tags for the words coresponding to the index lists,
  taking care of shifting indexes appropriately after multi-word substitutions
  NOTE: this assumes non-overlapping seqs!
  """
  words_out = words
  dj = 0
  for i in np.argsort(seqs):
    words_out = tag_seq(words_out, map(lambda j : j - dj, seqs[i]), tags[i])
    dj += len(seqs[i]) - 1
  return words_out

def apply_rules(relation_id, rule_obj, f, boolean_only=True):
  """
  Takes as input a tuple containing (rule_label, default_weight, heuristic_priority, rules)
  Where rules is a list of rules which are each either a pattern or a (pattern, weight) tuple/list
  Applies f to the pattern
  If true, yields a Label object, with the rule's weight or else the rule_obj's default weight
  If boolean_only=True, then just takes sign of weight
  """
  rule_id_base, w, hp, rules = rule_obj
  for rid,rule in enumerate(rules):
    if type(rule) == list or type(rule) == tuple:
      p, w = rule
    else:
      p = rule
    if f(p):
      yield Label(
        relation_id=relation_id,
        rule_id='%s:%s' % (rule_id_base, rid),
        rule_verbose='%s:%s' % (rule_id_base, re.sub(r'\W+', '_', re.escape(p))),
        heuristic_priority=hp,
        heuristic_priority_2=rid,
        label=int(np.sign(w)) if boolean_only else w)

def apply_rgx_rules(relation_id, rule_triple, string, flags=re.I):
  return apply_rules(relation_id, rule_triple, lambda p : re.search(p, string, flags=flags) is not None)

def apply_set_rules(relation_id, rule_triple, word_set):
  return apply_rules(relation_id, rule_triple, lambda x : x in word_set)

CHARITE_SUP_RGX = (
  'CHARITE_SUP_RGX',  # Rule supertype label
  1,                  # Rule default weight
  10,                 # Rule heuristic priority- we set to emulate pre-DP version of DSR code!
  [
    r'(mutat|delet|duplicat|truncat|SNP).*caus'
  ])

POS_RGX = (
  'POS_RGX',
  1,
  12,
  [
    #r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*(implicated?|found).*{{P}}',
    #r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*cause.*{{P}}', 
    #r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*{{G}}.*described.*(patient|family).*{{P}}',
    #r'.*patient.*{{G}}.*present with.*clinical.*{{P}}.*',
    #r'(single nucleotide polymorphisms|SNPs) in {{G}}.*cause.*{{P}}',
    #r'(mutation|deletion).*{{G}}.*described.*patients.*{{P}}',
    #('{{P}}.*(are|is) (attributable to|due to|caused by|result of).*{{G}}', 0.7),
    #r'known {{G}} mutation',
    #r'{{G}}.*responsible for.*{{P}}',
    #r'homozygous for {{G}} mutation.*{{P}}',
    #r'{{G}}\s*-\s*related {{P}}',
    #r'{{G}} symptoms (include|are|consist of).*{{P}}',
    #r'{{P}} results from.*{{G}}'
  ])

# NOTE: In the original "heuristic prioritization" implementation, 'phrases' were prioritized over
# regexes... this was not really an intentional design choice (I think) as much as arbitrary compromise
# However we should put phrases before regexes here to replicate
NEG_RGX = (
  'NEG_RGX',
  -1,
  4,
  [
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
    'mouse',
    'mice',
    'to find out',
    'inconclusive',
    'further analysis',
    'but not',
    'deficiency',
    'activity',
    'unravel',
    'how',
    'fish',
    'sheep',
    'cattle',
    'dachshund',
    'variance',
    'gwas',
    'association study',
    'possible association',
    'to investigate',
    'could reveal',
    'to determine',
    'unclear',
    'hypothesize',
    'to evaluate',
    'plasma',
    'expression',
    'to detect',
    'to find out',
    'inconclusive',
    'further analysis',
    'association',
    'associated',
    #r'to analyze',
    #'could not determine',
    #'unknown',
    #'needs',
    #'our aim',
    #'suggests',
    #'possible',
    #'potential role',
    #'conflicting results',
    r'{{P}}.*not.*cause.*{{G}}',
    r'{{G}}.*not.*cause.*{{P}}',
    r'\?\s*$',
    r'to determine',
    r'to evaluate',
    r'to investigate',
    r'we investigated',
    r'we examined',
    r'to examine',
    r'we requested',
    'to study',
    'indicating that',
    '\d+ h ',
    r'to assess',
    r'^\s*here we define',
    r'whether',
    'unlikely.*{{G}}.*{{P}}',
    '{{P}}.*not due to.*{{G}}',
    '{{G}}.*linked to.*{{P}}',
    'attracted.*interest',
    'target'
    #r'^\s*To establish'
    #r'^\s*To determine',
    #r'^\s*To evaluate',
    #r'^\s*To investigate',
    #r'^\s*To analyze',
    #r'^\s*To study',
    #r'^\s*To asses',
    #r'^\s*We evaluated',
    #r'^\s*We investigated',
    #r'^\s*We analyzed',
    #r'^\s*We studied',
    #r'^Although',
    #r'^However',
    #r'{{P}}.*not caused by.*{{G}}',
    #r'{{G}}.*not.*cause of.*{{P}}',
  ])

POS_PATH_BTWN = (
  'POS_PATH_BTWN',
  1,
  14,
  [
    #'responsible',
    #'attributable',
    #'had',
    #'include'
  ])

NEG_PATH_BTWN = (
  'NEG_PATH_BTWN',
  -1,
  6,
  [
    #'unlikely',
    #'suggest',
    #'possible',
    #'role',
    #'associate',
    #'unknown',
    #'potential'
  ])

NEG_VB_MOD = (
  'NEG_VB_MOD',
  -1,
  5,
  [
    'neg'
  ])

NEG_G_DEP_NB = (
  'NEG_G_DEP_NB',
  -1,
  7,
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
   'deficiency',
   'exclude'
  ])

POS_G_DEP_NB = (
  'POS_G_DEP_NB',
  1,
  15,
  [
    #'known'
  ])

NEG_P_DEP_NB = (
  'NEG_P_DEP_NB',
  -1,
  8,
  [
    'without',
    'except'
  ])

POS_P_DEP_NB = (
  'POS_P_DEP_NB',
  1,
  16,
  [])

def generate_labels(r, root):
  """Generate the Label objects produced by each applicable rule"""
  cids = [r.gene_wordidxs, r.pheno_wordidxs]
  seq = ' '.join(tag_seqs(r.words, cids, ['G', 'P']))
  generators = []
  
  # RULE over sequence + charite: Label T if (a) in charite pairs and (b) matches regex
  if (r.pheno_entity, r.gene_name) in CHARITE_PAIRS:
    generators.append(apply_rgx_rules(r.relation_id, CHARITE_SUP_RGX, seq))
  
  # RULE over sequence: Label if *any part* of full sentence matches regex
  generators.append(apply_rgx_rules(r.relation_id, POS_RGX, seq))
  generators.append(apply_rgx_rules(r.relation_id, NEG_RGX, seq))
  
  # RULE over dep-tree: Label based on path between
  btwn = Ngrams(Between(Mention(0), Mention(1)), 'lemma', 1).result_set(root, cids)
  generators.append(apply_set_rules(r.relation_id, POS_PATH_BTWN, btwn))
  generators.append(apply_set_rules(r.relation_id, NEG_PATH_BTWN, btwn))

  # RULE over dep-tree: Label based on matches of modifiers of VBs on the shortest path between
  vb_mods = Ngrams(Children(Filter(Between(Mention(0), Mention(1)), 'pos', 'VB')), 'dep_label', 1).result_set(root, cids)
  generators.append(apply_set_rules(r.relation_id, NEG_VB_MOD, vb_mods))

  # RULE over dep-tree:Label if word matches a node within distance D of G / P
  neighbors = Compile([
    Ngrams(LeftSiblings(Mention(0)), 'lemma', 1),
    Ngrams(RightSiblings(Mention(0)), 'lemma', 1),
    Ngrams(Parents(Mention(0), 1), 'lemma', 1),
    Ngrams(Children(Mention(0)), 'lemma', 1)
  ])
  g_nbs = neighbors.result_set(root, [r.gene_wordidxs])
  generators.append(apply_set_rules(r.relation_id, NEG_G_DEP_NB, g_nbs))
  generators.append(apply_set_rules(r.relation_id, POS_G_DEP_NB, g_nbs))

  p_nbs = neighbors.result_set(root, [r.pheno_wordidxs])
  generators.append(apply_set_rules(r.relation_id, NEG_P_DEP_NB, p_nbs))
  generators.append(apply_set_rules(r.relation_id, POS_P_DEP_NB, p_nbs))

  # Return a generator / iterable
  return chain.from_iterable(generators)

def supervise(r):
  """Given an input row, return Label objects"""
  # If G or P is false, exclude as a candidate
  if r.gene_is_correct != False and r.pheno_is_correct != False:

    # Get XML tree here
    # TODO: Move to preprocessing
    s = CoreNLPSentence(r.words, r.lemmas, r.poses, r.dep_paths, r.dep_parents)
    xt = corenlp_to_xmltree(s)

    # Perform supervision
    for label in generate_labels(r, xt.root):
      yield label

# Run extractor
if __name__ == '__main__':
  CHARITE_PAIRS = read_charite_supervision(read_hpo_dag())
  run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=supervise)
