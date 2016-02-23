#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib

parser = util.RowParser([
          ('relation_id', 'text'),
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('gene_mention_id', 'text'),
          ('gene_wordidxs', 'int[]'),
          ('pheno_mention_id', 'text'),
          ('pheno_wordidxs', 'int[]'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]')])


Feature = namedtuple('Feature', ['doc_id', 'section_id', 'relation_id', 'name'])

bad_features = ['STARTS_WITH_CAPITAL_[True_True]', 'NGRAM_1_[to]', 'NGRAM_1_[a]', 'NGRAM_1_[and]', 'NGRAM_1_[in]', 'IS_INVERTED', 
                'INV_NGRAM_1_[or]']
inv_bad_features = []
for f in bad_features:
  inv_bad_features.append('INV_' + f)
bad_features.extend(inv_bad_features)

def create_ners_between(gene_wordidxs, pheno_wordidxs, ners):
  if gene_wordidxs[0] < pheno_wordidxs[0]:
    start = max(gene_wordidxs) + 1
    end = min(pheno_wordidxs) - 1
  else:
    start = max(pheno_wordidxs) + 1
    end = min(gene_wordidxs) - 1
  prefix = 'NERS_BETWEEN_'
  nonnull_ners = []
  for i in xrange(start, end+1):
    ner = ners[i]
    if ner != 'O':
      nonnull_ners.append('[' + ner + ']')
  rv = prefix + '_'.join(nonnull_ners)
  return [rv]
          
def get_features_for_candidate(row):
  """Extract features for candidate mention- both generic ones from ddlib & custom features"""
  features = []
  f = Feature(doc_id=row.doc_id, section_id=row.section_id, relation_id=row.relation_id, name=None)
  dds = util.create_ddlib_sentence(row)

  # (1) GENERIC FEATURES from ddlib
  gene_span = ddlib.Span(begin_word_id=row.gene_wordidxs[0], length=len(row.gene_wordidxs))
  pheno_span = ddlib.Span(begin_word_id=row.pheno_wordidxs[0], length=len(row.pheno_wordidxs))
  for feat in ddlib.get_generic_features_relation(dds, gene_span, pheno_span):
    if feat in bad_features:
      continue
    features.append(f._replace(name=feat))
  # WITH these custom features, I get a little LESS precision and a little MORE recall (!)
  #features += [f._replace(name=feat) for feat in create_ners_between(row.gene_wordidxs, row.pheno_wordidxs, row.ners)]
  return features

# Helper for loading in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

if __name__ == '__main__':
  ddlib.load_dictionary(onto_path("manual/genepheno_keywords.txt"), dict_id="gp_relation_kws")
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_candidate)
