#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('mention_id', 'text'),
          ('mention_wordidxs', 'int[]')])

def get_features_for_candidate(row):
  """Extract features for candidate mention- both generic ones from ddlib & custom features"""
  features = []
  dds = util.create_ddlib_sentence(row)

  # (1) GENERIC FEATURES from ddlib
  span = ddlib.Span(begin_word_id=row.mention_wordidxs[0], length=len(row.mention_wordidxs))
  features += [(row.doc_id, row.mention_id, feat) \
                    for feat in ddlib.get_generic_features_mention(dds, span)]

  # (2) Add the closest verb by raw distance
  verb_idxs = [i for i,p in enumerate(row.poses) if p.startswith("VB")]
  if len(verb_idxs) > 0:
    dists = filter(lambda d : d[0] > 0, \
                   [(min([abs(i-j) for j in row.mention_wordidxs]), i) for i in verb_idxs])
    if len(dists) > 0:
      verb = row.lemmas[min(dists)[1]]
      features.append((row.doc_id, row.mention_id, 'NEAREST_VERB_[%s]' % (verb,)))
  return features

# Load in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

if __name__ == '__main__':
  ddlib.load_dictionary(onto_path('manual/pheno_sentence_keywords.tsv'), dict_id='pheno_kws')
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_candidate)
