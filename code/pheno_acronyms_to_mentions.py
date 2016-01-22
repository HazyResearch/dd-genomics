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
          ('pa_abbrevs', 'text[]'),
          ('pheno_entities', 'text[]'),
          ('pa_section_ids', 'text[]'),
          ('pa_sent_ids', 'int[]')])

ExpandedRow = namedtuple('ExpandedRow', [
          'doc_id',
          'section_id',
          'sent_id',
          'words',
          'lemmas',
          'poses',
          'ners',
          'pa_abbrev',
          'pheno_entity',
          'pa_section_id',
          'pa_sent_id'])



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

def expand_array_rows(array_row):
  for i, pa_abbrev in enumerate(array_row.pa_abbrevs):
    row = ExpandedRow(doc_id = array_row.doc_id,
                      section_id = array_row.section_id,
                      sent_id = array_row.sent_id,
                      words = array_row.words,
                      lemmas = array_row.lemmas,
                      poses = array_row.poses,
                      ners = array_row.ners,
                      pa_abbrev = pa_abbrev,
                      pheno_entity = array_row.pheno_entities[i],
                      pa_section_id = array_row.pa_section_ids[i],
                      pa_sent_id = array_row.pa_sent_ids[i])
    yield row


### CANDIDATE EXTRACTION ###
SR = config.PHENO_ACRONYMS['SR']

def extract_candidate_mentions(row):
  """Extracts candidate phenotype mentions from an input row object"""
  mentions = []

  for i, word in enumerate(row.words):
    if word == row.pa_abbrev:
      mention_id = '%s_%s_%d_%d' %  \
           (row.doc_id, \
            row.section_id, \
            row.sent_id, \
            i)
      subtype = '%s_%s_%d_%s' % (row.doc_id, row.pa_section_id, row.pa_sent_id, row.pa_abbrev)
      m = Mention(None, row.doc_id, row.section_id, row.sent_id,
          [i], mention_id, "ABBREV", subtype, row.pheno_entity,
          [word], True)
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
      mention_id = '%s_%s_%d_%d' %  \
           (row.doc_id, \
            row.section_id, \
            row.sent_id, \
            i)
      subtype = '%s_%s_%d_%s' % (row.doc_id, row.pa_section_id, row.pa_sent_id, row.pa_abbrev)
      m = Mention(None, row.doc_id, row.section_id, row.sent_id, 
          [i], mention_id, 'ABBREV_RAND_NEG', subtype, None, [word], False)
      neg += 1
  return mentions

if __name__ == '__main__':
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

  pos = 0
  neg = 0

  # Read TSV data in as Row objects
  for line in sys.stdin:
    array_row = parser.parse_tsv_row(line)
    abbrevs = set()
    for row in expand_array_rows(array_row):
      if row.pa_abbrev in abbrevs:
        continue
      abbrevs.add(row.pa_abbrev)
  
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
#!/usr/bin/env python
