#! /usr/bin/env python

import collections
import extractor_util as util
import data_util as dutil
import dep_util as deps
import os
import random
import re
import sys
import config
import string
from util import latticelib

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
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
            'relation_subtype'])

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
  with open('%s/onto/data/canon_phenotype_to_gene.map' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_name = line.strip().split('\t')
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      for h in hpo_ids:
        supervision_pairs.add((h,gene_name))
  return supervision_pairs

# count_g_or_p_false_none = 0 
# count_adjacent_false_none = 0 

non_alnum = re.compile('[\W_]+')
def create_supervised_relation(row, superv_diff, SR, HF, charite_pairs):
  """
  Given a Row object with a sentence and several gene and pheno objects, create and 
  supervise a Relation output object for the ith gene and jth pheno objects
  Note: outputs a list for convenience
  Also includes an input for d = pos - neg supervision count, for neg supervision
  """
  gene_mention_id = row.gene_mention_id
  gene_name = row.gene_name
  gene_wordidxs = row.gene_wordidxs
  gene_is_correct = row.gene_is_correct
  pheno_mention_id = row.pheno_mention_id
  pheno_entity = row.pheno_entity
  pheno_wordidxs = row.pheno_wordidxs
  pheno_is_correct = row.pheno_is_correct
  gene = row.gene_name
  pheno = ' '.join([row.words[i] for i in row.pheno_wordidxs])

  phrase = ' '.join(row.words)
  lemma_phrase = ' '.join(row.lemmas)

  relation_id = '%s_%s' % (gene_mention_id, pheno_mention_id)
  r = Relation(None, relation_id, row.doc_id, row.section_id, row.sent_id, gene_mention_id, gene_name, \
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None, None)  

  
  config = latticelib.Config()
  sentence_index = latticelib.create_sentence_index(row)
  print >>sys.stderr, sentence_index
  # mentions = self.extract_candidates(sentence_index, doc, self)
  # for featurizer in config.featurizers:
  #     mentions = featurizer(mentions, sentence_index, doc, self)
  # mentions = self.supervise(mentions, sentence_index, doc, self)
  assert False

  
  # Return GP relation object
  return r

def supervise(supervision_rules, hard_filters):
  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  pos_count = 0
  neg_count = 0
  # load in static data
  CHARITE_PAIRS = read_supervision()
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    relation = create_supervised_relation(row, superv_diff=pos_count-neg_count, SR=supervision_rules, HF=hard_filters, charite_pairs=CHARITE_PAIRS)
    
    if relation:
      if relation.is_correct == True:
        pos_count += 1
      elif relation.is_correct == False:
        neg_count += 1
      util.print_tsv_output(relation)
  # sys.stderr.write('count_g_or_p_false_none: %s\n' % count_g_or_p_false_none)
  # sys.stderr.write('count_adjacent_false_none: %s\n' % count_adjacent_false_none)

genepheno_dicts = {
    'mutation' : ['mutation', 'allele', 'variant'],
    'serum' : ['serum', 'level', 'elevated', 'plasma'],
}

pos_patterns = {
    '[rel[1]] -nsubjpass-> cause -nmod-> mutation -nmod-> [rel[0]]',
}

neg_patterns = {
    'possible _ association',
}

strong_pos_patterns = {
    '[rel[1]] -nsubjpass-> cause -nmod-> mutation -nmod-> [rel[0]]',
}

strong_neg_patterns = {
    'possible _ association',
}

if __name__ == '__main__':
  supervision_rules = config.GENE_PHENO_ASSOCIATION['SR']
  hard_filters = config.GENE_PHENO_ASSOCIATION['HF']
  supervise(supervision_rules, hard_filters)
  
  # Configure the extractor
  config = latticelib.Config()

  config.add_dicts(genepheno_dicts)
  config.set_pos_patterns(pos_patterns)
  config.set_neg_patterns(neg_patterns)
  config.set_strong_pos_patterns(strong_pos_patterns)
  config.set_strong_neg_patterns(strong_neg_patterns)
  config.set_candidate_generator(read_candidate)
  config.set_pos_supervision_phrases([])
  config.set_neg_supervision_phrases([])
  # config.set_feature_patterns(feature_patterns)
  # config.add_featurizer(ddlib_featurizer)
  config.NGRAM_WILDCARD = False
  config.PRINT_SUPV_RULE = True

  config.run()

