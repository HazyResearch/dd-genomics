#!/usr/bin/env python
import collections
import extractor_util as util
import data_util as dutil
import random
import re
import os
import sys
import string
import config
import dep_util as deps
from gene_extract_candidates import create_supervised_mention
import abbreviations

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
            'short_wordidxs',
            'long_wordidxs',
            'mention_id',
            'mention_supertype',
            'mention_subtype',
            'abbrev_word',
            'definition_words',
            'is_correct'])

### CANDIDATE EXTRACTION ###
HF = config.GENE['HF']
SR = config.GENE['SR']


def extract_candidate_mentions(row, pos_count, neg_count):
  phrase_to_genes = CACHE['phrase_to_genes']
  lower_phrase_to_genes = CACHE['lower_phrase_to_genes']
  mentions = []
  for (isCorrect, abbrev, definition) in abbreviations.getabbreviations(row.words):
    m = create_supervised_mention(row, isCorrect, abbrev, definition)
    mentions.append(m)
  return mentions
 
### DISTANT SUPERVISION ###
VALS = config.PHENO_ACRONYMS['vals']
def create_supervised_mention(row, isCorrect, (startAbbrev, stopAbbrev, abbrev), (startDefinition, stopDefinition, definition)):
  assert stopAbbrev == startAbbrev + 1
  mid = '%s_%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id, startAbbrev)
  [
            'dd_id',
            'doc_id',
            'section_id',
            'sent_id',
            'short_wordidxs',
            'long_wordidxs',
            'mention_id',
            'mention_supertype',
            'mention_subtype',
            'abbrev_word',
            'definition_words',
            'is_correct']
  m = Mention(None, row.doc_id, row.section_id, 
              row.sent_id, xrange(startAbbrev, stopAbbrev+1), 
              xrange(startDefinition, stopDefinition + 1), 
              mid, None, None, abbrev, definition, isCorrect);
  return m

def read_gene_to_full_name():
  rv = {}
  with open(onto_path('data/gene_names.tsv')) as f:
    for line in f:
      parts = line.split('\t')
      assert len(parts) == 2, parts
      geneAbbrev = parts[0]
      geneFullName = parts[1]
      assert geneAbbrev not in rv, geneAbbrev
      rv[geneAbbrev] = geneFullName
  return rv

if __name__ == '__main__':
  # load static data
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)
  CACHE['gene_to_full_name'] = read_gene_to_full_name()
  
  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  pos_count = 0
  neg_count = 0
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    # Skip row if sentence doesn't contain a verb, contains URL, etc.
    if util.skip_row(row):
      continue

    # Find candidate mentions & supervise
    try:
      mentions = extract_candidate_mentions(row, pos_count, neg_count)
    except IndexError:
      util.print_error("Error with row: %s" % (row,))
      continue

    pos_count += len([m for m in mentions if m.is_correct])
    neg_count += len([m for m in mentions if m.is_correct is False])

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
