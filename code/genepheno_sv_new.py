#! /usr/bin/env python

import collections
from util import extractor_util as eutil
from util import data_util as dutil
import re
import sys
import config
from util import clf_util

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
            'misc'])

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
               gene_wordidxs, pheno_mention_id, pheno_entity, pheno_wordidxs, None, None, None, [], {})
  return r

if __name__ == '__main__':
  supervision_rules = config.GENE_PHENO_ASSOCIATION['SR']
  hard_filters = config.GENE_PHENO_ASSOCIATION['HF']
  for line in sys.stdin:
      row = parser.parse_tsv_row(line)
      cand = [row.gene_wordidxs, row.pheno_wordidxs]
      relation = read_candidate(row)
      sentence_index = clf_util.create_sentence_index(row)
      relation = clf_util.featurize(relation, cand, sentence_index, feature_patterns, [], genepheno_dicts)
      relation = clf_util.supervise(relation, cand, sentence_index, [], [], pos_patterns, neg_patterns, genepheno_dicts)      
      eutil.print_tsv_output(relation)