#!/usr/bin/env python
from collections import namedtuple
import extractor_util as util
import os
import sys
import ddlib
import re
from config import FEATURES

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
          ('mention_type', 'text'),
          ('mention_wordidxs', 'int[]')])

Feature = namedtuple('Feature', ['doc_id', 'mention_id', 'name'])

ENSEMBL_TYPES = ['NONCANONICAL', 'CANONICAL', 'REFSEQ']


def get_features_for_row(row):
  OPTS = FEATURES['gene']
  features = []
  f = Feature(doc_id=row.doc_id, mention_id=row.mention_id, name=None)

  # (1) Get generic ddlib features
  sentence = util.create_ddlib_sentence(row)
  span = ddlib.Span(begin_word_id=row.mention_wordidxs[0], length=len(row.mention_wordidxs))
  generic_features = [f._replace(name=feat) for feat in ddlib.get_generic_features_mention(sentence, span)]

  # Optionally filter out some generic features
  if 'exclude_generic' in OPTS:
    generic_features = filter(lambda feat : not feat.startswith(tuple(OPTS['exclude_generic'])), generic_features)

  features += generic_features
  
  # (2) Include gene type as a feature
  # Note: including this as feature creates massive overfitting, for obvious reasons
  # We need neg supervision of canonical & noncanonical symbols, then can / should try adding this feature
  """
  for t in ENSEMBL_TYPES:
    if re.search(re.escape(t), row.mention_type, flags=re.I):
      features.append(f._replace(name='GENE_TYPE[%s]' % t))
      break
  """
  return features

if __name__ == '__main__':
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_row)
