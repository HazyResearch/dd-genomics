#! /usr/bin/env python

import collections
from util import extractor_util as eutil
from util import data_util as dutil
import re
import sys
import config
from util import clf_util
from dep_alignment.alignment_util import row_to_canonical_match_tree, DepParentsCycleException, OverlappingCandidatesException, RootException, canonicalize_row
from dep_alignment.multi_dep_alignment import MultiDepAlignment
import os
import random
import time

# This defines the Row object that we read in to the extractor
parser = eutil.RowParser([
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
            ('dep_parents', 'int[]'),
            ('ners', 'text')])

ds_parser = eutil.RowParser([
            ('words', 'text[]'),
            ('lemmas', 'text[]'),
            ('poses', 'text[]'),
            ('dep_paths', 'text[]'),
            ('dep_parents', 'int[]'),
            ('gene_wordidxs', 'int[]'),
            ('pheno_wordidxs', 'int[]')])
# This defines the output Relation object
Relation = collections.namedtuple('Relation', [
            'dd_id',
            'relation_id',
            'doc_id',
            'section_id',
            'sent_id',
            'gene_mention_id',
            'gene_name',
            'gene_wordidxs',
            'pheno_mention_id',
            'pheno_entity',
            'pheno_wordidxs',
            'is_correct',
            'relation_supertype',
            'relation_subtype',
            'features',
            'matching_scores',
            'rescores'])

HPO_DAG = dutil.read_hpo_dag()

def replace_opts(opts, replaceList):
  ret = {}
  for name in opts:
    strings = opts[name]
    for (pattern, subst) in replaceList:
      if name.endswith('rgx'):
        subst = re.escape(subst)
      strings = [s.replace(pattern, subst) for s in strings]
    ret[name] = strings
  return ret

def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/canon_phenotype_to_gene.map' % eutil.APP_HOME) as f:
    for line in f:
      hpo_id, gene_name = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      for h in hpo_ids:
        supervision_pairs.add((h, gene_name))
  return supervision_pairs

# count_g_or_p_false_none = 0
# count_adjacent_false_none = 0

non_alnum = re.compile('[\W_]+')

genepheno_dicts = {
    # dicts have to be ONE-WORD!!!
    'mutation' : ['mutation', 'allele', 'variant'],
    'serum' : ['serum', 'level', 'elevated', 'plasma'],
}

pos_patterns = {
    # '[cand[1]] -nsubjpass-> cause -nmod-> mutation -nmod-> [cand[0]]',
    '[cand[1]] -nsubjpass-> cause -nmod-> mutation',
}

neg_patterns = {
    'association',
}

feature_patterns = ['[cand[1]] __ _ __ _ __ _ __ [cand[0]]']

def read_candidate(row):
  gene_mention_id = row.gene_mention_id
  gene_name = row.gene_name
  gene_wordidxs = row.gene_wordidxs
  pheno_mention_id = row.pheno_mention_id
  pheno_entity = row.pheno_entity
  pheno_wordidxs = row.pheno_wordidxs

  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.section_id, row.sent_id, gene_mention_id, gene_name, \
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None, None, [], None, None)
  return r

if __name__ == '__main__':
  # supervision_rules = config.GENE_PHENO_ASSOCIATION['SR']
  # hard_filters = config.GENE_PHENO_ASSOCIATION['HF']
  app_home = os.environ['APP_HOME']
  match_trees = []
  with open(app_home + '/true_causation_sentences1.tsv') as f:
    for line in f:
      row = ds_parser.parse_tsv_row(line)
      try:
        match_trees.append(row_to_canonical_match_tree(row, [row.gene_wordidxs, row.pheno_wordidxs]))
      except (DepParentsCycleException, OverlappingCandidatesException, RootException):
        continue
  mt_root1, match_tree1 = match_trees[0]
  for mt_root0, match_tree0 in match_trees[1:]:
    # for i, mc in enumerate(match_tree1):
    #   print >>sys.stderr, str(i+1) + ": " + str(mc)
    mda = MultiDepAlignment(mt_root0, match_tree0, mt_root1, match_tree1, 2, \
                                [set(['disease', 'disorder']), \
                                 set(['mutation', 'variant', 'allele', 'polymorphism']), \
                                 set(['case', 'patient']), \
                                 set(['identify', 'report', 'find', 'detect']), \
                                 set(['cause', 'associate', 'link', 'lead'])])
    mt_root1, match_tree1 = mda.get_match_tree()
    
  # mt_root1, match_tree1 = match_trees[0]
  lc = 0
  start_time = time.time()
  # with open(app_home + '/match_paths%d.txt' % random.randint(0, 100000), 'a') as f:
  for line in sys.stdin:
    lc += 1
    row = parser.parse_tsv_row(line)
    if row.gene_is_correct == False or row.pheno_is_correct == False:
      continue
    try:
      mt_root2, match_tree2 = row_to_canonical_match_tree(row, [row.gene_wordidxs, row.pheno_wordidxs])
      assert len(match_tree2) <= len(row.words) + 1, (len(row.words), len(match_tree2), row.words, match_tree2) 
    except (DepParentsCycleException, OverlappingCandidatesException, RootException):
      continue
    matching_scores = []
    rescores = []
    # for (mt_root1, match_tree1) in match_trees:
    mda = MultiDepAlignment(mt_root1, match_tree1, mt_root2, match_tree2, 2, \
                            [set(['disease', 'disorder']), \
                             set(['mutation', 'variant', 'allele', 'polymorphism']), \
                             set(['case', 'patient']), \
                             set(['identify', 'report', 'find', 'detect']), \
                             set(['cause', 'associate', 'link', 'lead'])])
    # mda.print_matched_lemmas(f)
    # mda.print_match_path(f)
    score1 = mda.overall_score()
    score2 = mda.rescore([(set(['cause', 'lead']), set(['associate', 'link']), -20)])
    r = read_candidate(row)
    matching_scores.append(int(score1))
    rescores.append(int(score1 + score2))
    # end for
    eutil.print_tsv_output(r._replace(matching_scores=matching_scores, rescores=rescores))
  end_time = time.time()
  if lc != 0:
    print >>sys.stderr, "Number of lines: %d, Time per line: %f seconds" % (lc, (end_time - start_time) / (float(lc)))
