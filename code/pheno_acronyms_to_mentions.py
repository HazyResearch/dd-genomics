#!/usr/bin/env python

from collections import defaultdict, namedtuple
import sys
import re
import os
import random
from itertools import chain
import extractor_util as util
import data_util as dutil
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
          ('pa_abbrev', 'text'),
          ('pa_wordidxs', 'int[]')
          ('pheno_entity', 'text'),
          ('pa_supertype', 'text'),
          ('pa_subtype', 'text'),
          ('pa_is_correct', 'boolean')])


# This defines the output Mention object
Mention = namedtuple('Mention', [
            'dd_id',
            'doc_id',
            'section_id',
            'sent_id',
            'wordidxs',
            'mention_id',
            'mention_supertype',
            'mention_subtype',
            'entity',
            'words',
            'is_correct'])


### CANDIDATE EXTRACTION ###
HF = config.PHENO['HF']
SR = config.PHENO['SR']

def extract_candidate_mentions(row):
  """Extracts candidate phenotype mentions from an input row object"""
  mentions = []
  if row.pa_is_correct == False:
    return []

  for word in row.words:
    if word == row.abbrev:
      mentions.append((None, row.doc_id, row.section_id, row.sent_id,
          row.
  
  return mentions

if __name__ == '__main__':
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

  # Read TSV data in as Row objects
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    # Skip row if sentence doesn't contain a verb, contains URL, etc.
    if util.skip_row(row):
      continue

    # find candidate mentions & supervise
    mentions = extract_candidate_mentions(row)
    if SR.get('rand-negs'):
      mentions += generate_rand_negatives(row, mentions)

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
