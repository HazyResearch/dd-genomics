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
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]')])


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
  

def create_supervised_mention(row, i):
  """Given a Row object consisting of a sentence, create & supervise a Mention output object"""
  word = row.words[i]
  mid = '%s_%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id, i)
  m = Mention(None, row.doc_id, row.section_id, row.sent_id, [i], \
              mid, None, None, word, None)
  
  return m

def extract_candidate_mentions(row):
  mentions = []
  for i, word in enumerate(row.words):
    m = create_supervised_mention(row, i, gene_name=word)
    if m:
      mentions.append(m)
  return mentions

if __name__ == '__main__':
  pos_count = 0
  neg_count = 0
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    mentions = extract_candidate_mentions(row)
    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
