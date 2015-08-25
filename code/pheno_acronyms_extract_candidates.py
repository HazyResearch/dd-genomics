#!/usr/bin/env python
import collections
import os
import sys

import abbreviations
import config
import extractor_util as util
from gene_extract_candidates import create_supervised_mention
import levenshtein


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
# HF = config.PHENO_ACRONYMS['HF']
SR = config.PHENO_ACRONYMS['SR']

def extract_candidate_mentions(row, pos_count, neg_count):
  mentions = []
  for (is_correct, abbrev, definition, detector_message) in abbreviations.getabbreviations(row.words):
    m = create_supervised_mention(row, is_correct, abbrev, definition, detector_message)
    ':type m: Mention'
    mentions.append(m)
  return mentions

### DISTANT SUPERVISION ###
VALS = config.PHENO_ACRONYMS['vals']
def create_supervised_mention(row, is_correct, 
                              (start_abbrev, stop_abbrev, abbrev), 
                              (start_definition, stop_definition, 
                               definition), detector_message):
  assert stop_abbrev == start_abbrev + 1
  mid = '%s_%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id, start_abbrev)
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
  gene_to_full_name = CACHE['gene_to_full_name']
  if is_correct:
    supertype = 'TRUE_DETECTOR'
    subtype = None
  elif is_correct is False:
    supertype = 'FALSE_DETECTOR'
    subtype = detector_message
  else:
    supertype = 'DETECTOR_OMITTED_SENTENCE'
    subtype = None
  if is_correct and abbrev in SR['short_words']:
    is_correct = False
    supertype = 'FALSE_SHORT_WORD'
    subtype = None
  close_matches = difflib.get_close_matches(' '.join(definition), CACHE['phenos'], n=1, cutoff=SR['difflib.pheno_cutoff    '])
  if is_correct and close_matches:
    full_gene_name = gene_to_full_name[abbrev];
    ld = levenshtein.levenshtein(full_gene_name.lower(), ' '.join(definition).lower())
    supertype = 'TRUE_PHENO'
    subtype = close_matches[0]
  else:
    is_correct = False
    supertype = 'FALSE_NOT_A_PHENO'
    subtype = None
  m = Mention(None, row.doc_id, row.section_id,
              row.sent_id, [i for i in xrange(start_abbrev, stop_abbrev + 1)],
              [i for i in xrange(start_definition, stop_definition + 1)],
              mid, supertype, subtype, abbrev, definition, is_correct);
  return m

if __name__ == '__main__':
  # load static data
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)
  CACHE['phenos'] = assert False, 'TODO'

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
    mentions = extract_candidate_mentions(row, pos_count, neg_count)

    pos_count += len([m for m in mentions if m.is_correct])
    neg_count += len([m for m in mentions if m.is_correct is False])

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)