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
          ('pheno_entity', 'text'),
          ('pa_doc_id', 'text'),
          ('pa_section_id', 'text'),
          ('pa_sent_id', 'int'),
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
SR = config.PHENO_ACRONYMS['SR']

def extract_candidate_mentions(row):
  """Extracts candidate phenotype mentions from an input row object"""
  mentions = []
  if row.pa_is_correct == False:
    return []

  for i, word in enumerate(row.words):
    if word == row.pa_abbrev:
      mention_id = '%s_%s_%d_%d_%d_ABBREV_%s' %  \
           (row.doc_id, \
            row.section_id, \
            row.sent_id, \
            i, \
            i, \
            row.pheno_entity)
      subtype = '%s_%s_%d_%s' % (row.pa_doc_id, row.pa_section_id, row.pa_sent_id, row.pa_abbrev)
      m = Mention(None, row.doc_id, row.section_id, row.sent_id,
          [i], mention_id, "ABBREV", subtype, row.pheno_entity,
          [word], row.pa_is_correct)
      mentions.append(m)
  
  return mentions

def generate_rand_negatives(row, pos, neg):
  mentions = []
  for i, word in enumerate(row.words):
    if neg >= pos:
      break
    if word == row.pa_abbrev:
      continue
    if word.isupper() and word.strip() != '-LRB-' and word.strip() != '-RRB-':
      mention_id = '%s_%s_%d_%d_%d_ABBREV_RAND_NEG_%s' %  \
           (row.doc_id, \
            row.section_id, \
            row.sent_id, \
            i, \
            i, \
            row.pheno_entity)
      subtype = '%s_%s_%d_%s' % (row.pa_doc_id, row.pa_section_id, row.pa_sent_id, row.pa_abbrev)
      m = Mention(None, row.doc_id, row.section_id, row.sent_id, 
          [i], mention_id, 'ABBREV_RAND_NEG', subtype, None, [word], False)
      mentions.append(m)
      neg += 1
  return mentions

if __name__ == '__main__':
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

  pos = 0
  neg = 0

  # Read TSV data in as Row objects
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    # Skip row if sentence doesn't contain a verb, contains URL, etc.
    if util.skip_row(row):
      continue

    # find candidate mentions & supervise
    mentions = extract_candidate_mentions(row)
    pos += len(mentions)
    if SR.get('rand-negs'):
      negs = generate_rand_negatives(row, pos, neg)
      neg += len(negs)
      mentions.extend(negs)

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
