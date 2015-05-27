#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib

Row = namedtuple('Row', ['doc_id', 'sent_id', 'words', 'lemmas', 'poses', 'ners',
            'dep_paths', 'dep_parents', 'mention_id', 'mention_wordidxs'])

def parse_input_row(line):
  tokens = line.split('\t')
  return Row(doc_id=tokens[0],
             sent_id=int(tokens[1]),
             words=util.tsv_string_to_list(tokens[2]),
             lemmas=util.tsv_string_to_list(tokens[3]),
             poses=util.tsv_string_to_list(tokens[4]),
             ners=util.tsv_string_to_list(tokens[5]),
             dep_paths=util.tsv_string_to_list(tokens[6]),
             dep_parents=util.tsv_string_to_list(tokens[7], func=int),
             mention_id=tokens[8],
             mention_wordidxs=util.tsv_string_to_list(tokens[9], func=int))

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

  # (3) Add the closest verb + its dep_path relation by dep_path distance
  # TODO: See if ddlib has dep path handling and/or build simple solution!
  # TODO: play around with more dep_path features in general!
  
  return features

# Load in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

if __name__ == '__main__':
  ddlib.load_dictionary(onto_path('manual/pheno_sentence_keywords.tsv'), dict_id='pheno_kws')
  util.run_main_tsv(row_parser=parse_input_row, row_fn=get_features_for_candidate)
