#!/usr/bin/env python
import collections
import extractor_util as util
import os
import sys

import ddlib


Row = collections.namedtuple(
    'Row', ['doc_id', 'sent_id', 'words', 'lemmas', 'poses', 'ners',
            'dep_paths', 'dep_parents', 'mention_id', 'wordidxs'])


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
             wordidxs=util.tsv_string_to_list(tokens[9], func=int))


def create_sentence(row):
  """Create a list of ddlib.Word objects from input row."""
  sentence = []
  for i, word in enumerate(row.words):
    sentence.append(ddlib.Word(
        begin_char_offset=None,
        end_char_offset=None,
        word=word,
        lemma=row.lemmas[i],
        pos=row.poses[i],
        ner=row.ners[i],
        dep_par=row.dep_parents[i],
        dep_label=row.dep_paths[i]))
  return sentence


def get_features_for_row(row):
  sentence = create_sentence(row)
  span = ddlib.Span(begin_word_id=row.wordidxs[0], length=len(row.wordidxs))
  return [(row.doc_id, row.mention_id, feat)
          for feat in ddlib.get_generic_features_mention(sentence, span) if not (feat.startswith("LEMMA_SEQ") or feat.startswith("WORD_SEQ"))]


def main():
  features = []
  for line in sys.stdin:
    features.extend(get_features_for_row(parse_input_row(line)))
  for feature in features:
    util.print_tsv_output(feature)


if __name__ == '__main__':
  main()
