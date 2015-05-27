#!/usr/bin/env python
import collections
import extractor_util as util
import os
import sys
import ddlib

Row = collections.namedtuple(
    'Row', ['doc_id', 'sent_id', 'words', 'lemmas', 'poses', 'ners',
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

def get_features_for_row(row):
  sentence = util.create_ddlib_sentence(row)
  span = ddlib.Span(begin_word_id=row.mention_wordidxs[0], length=len(row.mention_wordidxs))
  return [(row.doc_id, row.mention_id, feat) \
            for feat in ddlib.get_generic_features_mention(sentence, span) if not (feat.startswith("LEMMA_SEQ") or feat.startswith("WORD_SEQ"))]

if __name__ == '__main__':
  util.run_main_tsv(row_parser=parse_input_row, row_fn=get_features_for_row)
