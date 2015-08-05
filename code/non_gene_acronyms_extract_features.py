#!/usr/bin/env python
from collections import namedtuple
import extractor_util as util
import os
import sys
import ddlib
import re
import config

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('mention_id', 'text'),
          ('mention_type', 'text'),
          ('short_wordidxs', 'int[]'),
          ('long_wordidxs', 'int[]')])

Feature = namedtuple('Feature', ['doc_id', 'section_id', 'mention_id', 'name'])

ENSEMBL_TYPES = ['NONCANONICAL', 'CANONICAL', 'REFSEQ']


def get_features_for_row(row):
  OPTS = config.NON_GENE_ACRONYMS['F']
  features = []
  f = Feature(doc_id=row.doc_id, section_id=row.section_id, mention_id=row.mention_id, name=None)

  # (1) Get generic ddlib features
  sentence = util.create_ddlib_sentence(row)
  allWordIdxs = row.short_wordidxs + row.long_wordidxs
  start = min(allWordIdxs)
  length = max(allWordIdxs) - start
  span = ddlib.Span(begin_word_id=start, length=length)
  generic_features = [f._replace(name=feat) for feat in ddlib.get_generic_features_mention(sentence, span)]

  # Optionally filter out some generic features
  if OPTS.get('exclude_generic'):
    generic_features = filter(lambda feat : not feat.startswith(tuple(OPTS['exclude_generic'])), generic_features)

  features += generic_features
  
  return features

if __name__ == '__main__':
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_row)
