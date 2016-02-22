#!/usr/bin/env python
import collections
import extractor_util as util
import data_util as dutil
import random
import re
import os
import sys
import string
import dep_util as deps

CACHE = dict()  # Cache results of disk I/O


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
          ('dep_parents', 'int[]')])


# This defines the output Mention object
Mention = collections.namedtuple('Mention', [
            'dd_id',
            'doc_id',
            'section_id',
            'sent_id',
            'wordidxs',
            'mention_id',
            'mention_supertype',
            'mention_subtype',
            'word',
            'is_correct'])

def load_supervision():
  rv = {}
  with open('%s/onto/manual/split-words-sv.tsv' % os.environ['GDD_HOME']) as f:
    for line in f:
      line = line.split('\t')
      mention_id = line[0]
      label = line[1]
      if label == 't':
        rv[mention_id] = True
      else:
        rv[mention_id] = False
  return rv

def create_supervised_mention(row, i):
  """Given a Row object consisting of a sentence, create & supervise a Mention output object"""
  sv = load_supervision()
  word = row.words[i]
  mid = '%s_%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id, i)
  m = Mention(None, row.doc_id, row.section_id, row.sent_id, [i], \
              mid, None, None, word, None)
  if mid in sv:
    m = m._replace(is_correct=sv[mid])
  return m

def extract_candidate_mentions(row):
  mentions = []
  for i, word in enumerate(row.words):
    if word == ',' or word == 'whereas' or word == 'and' \
        or word == 'but' or word == 'while' or word == ';':
      m = create_supervised_mention(row, i)
      if m:
        mentions.append(m)
  return mentions

if __name__ == '__main__':
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    mentions = extract_candidate_mentions(row)
    for mention in mentions:
      util.print_tsv_output(mention)
