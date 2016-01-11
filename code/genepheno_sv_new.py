#! /usr/bin/env python

import collections
import extractor_util as eutil
import sys
from dep_alignment.alignment_util import row_to_canonical_match_tree, DepParentsCycleException, OverlappingCandidatesException, RootException
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
  app_home = os.environ['APP_HOME']
  match_trees = []
  with open(app_home + '/match_paths/match_paths%d.txt' % random.randint(0, 100000), 'a') as match_path_file:
    with open(app_home + '/true_causation_sentences2.tsv') as f:
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
                                   set(['case', 'patient', 'subject', 'family', 'boy', 'girl']), \
                                   set(['present', 'display', 'characterize']), \
                                   set(['nonsense', 'missense', 'frameshift']), \
                                   set(['identify', 'report', 'find', 'detect']), \
                                   set(['cause', 'associate', 'link', 'lead']),
                                   set(['mutation', 'inhibition']), \
                                   set(['recessive', 'dominant'])])
      mt_root1, match_tree1 = mda.get_match_tree()
      
    # mt_root1, match_tree1 = match_trees[0]
    mda.print_match_tree(match_path_file)
    lc = 0
    start_time = time.time()
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
                               set(['mutation', 'variant', 'allele', 'polymorphism', \
                                    'SNP', 'truncation', 'deletion', 'duplication']), \
                               set(['case', 'patient']), \
                               set(['identify', 'report', 'find', 'detect']), \
                               set(['cause', 'associate', 'link', 'lead', 'result']),
                               set(['mutation', 'inhibition', 'deficiency'])])
      # mda.print_matched_lemmas(match_path_file)
      print >>match_path_file, ' '.join(row.words)
      mda.print_match_tree(match_path_file)
      score1 = mda.overall_score()
      score2 = mda.rescore([(set(['cause', 'lead', 'result']), set(['associate', 'link']), -50),
                            (set(['mutation']), set(['inhibition', 'deficiency']), -50)])
      r = read_candidate(row)
      matching_scores.append(int(score1))
      rescores.append(int(score1 + score2))
      # end for
      eutil.print_tsv_output(r._replace(matching_scores=matching_scores, rescores=rescores))
    end_time = time.time()
    if lc != 0:
      print >>sys.stderr, "Number of lines: %d, time per line: %f seconds" % (lc, (end_time - start_time) / (float(lc)))
