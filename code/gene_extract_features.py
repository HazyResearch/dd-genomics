#!/usr/bin/env python
import collections
import extractor_util as util
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

def get_features_for_row(row):
  sentence = util.create_ddlib_sentence(row)
  span = ddlib.Span(begin_word_id=row.mention_wordidxs[0], length=len(row.mention_wordidxs))
  return [(row.doc_id, row.mention_id, feat) \
            for feat in ddlib.get_generic_features_mention(sentence, span) if not (feat.startswith("LEMMA_SEQ") or feat.startswith("WORD_SEQ"))]

if __name__ == '__main__':
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_row)
