#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib

parser = util.RowParser([
          ('relation_id', 'text'),
          ('doc_id', 'text'),
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
          ('dep_parents', 'int[]'),
          ('wordidxs', 'int[]')])

Feature = namedtuple('Feature', ['doc_id', 'relation_id', 'name'])
          
def get_features_for_candidate(row):
  """Extract features for candidate mention- both generic ones from ddlib & custom features"""
  features = []
  f = Feature(doc_id=row.doc_id, relation_id=row.relation_id, name=None)
  dds = util.create_ddlib_sentence(row)

  # (1) GENERIC FEATURES from ddlib
  gene_span = ddlib.Span(begin_word_id=row.gene_wordidxs[0], length=len(row.gene_wordidxs))
  pheno_span = ddlib.Span(begin_word_id=row.pheno_wordidxs[0], length=len(row.pheno_wordidxs))
  features += [f._replace(name=feat) \
                    for feat in ddlib.get_generic_features_relation(dds, gene_span, pheno_span)]

  # (2) Are the gene and pheno mentions directly adjacent?
  # TODO: buckets for distance between them > 0?
  """
  if row.gene_wordidxs[-1] == row.pheno_wordidxs[0] - 1 or row.gene_wordidxs[0] == row.pheno_wordidxs[-1] + 1:
    features.append(f._replace(name='G_P_ADJACENT'))
  """
  return features

# Helper for loading in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

if __name__ == '__main__':
  ddlib.load_dictionary(onto_path("manual/genepheno_keywords.txt"), dict_id="gp_relation_kws")
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_candidate)
