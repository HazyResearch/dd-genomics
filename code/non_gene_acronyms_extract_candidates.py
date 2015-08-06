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
# HF = config.NON_GENE_ACRONYMS['HF']
SR = config.NON_GENE_ACRONYMS['SR']

def extract_candidate_mentions(row, pos_count, neg_count):
  mentions = []
  for (is_correct, abbrev, definition, detector_message) in abbreviations.getabbreviations(row.words):
    m = create_supervised_mention(row, is_correct, abbrev, definition, detector_message)
    ':type m: Mention'
    mentions.append(m)
  return mentions

### DISTANT SUPERVISION ###
VALS = config.NON_GENE_ACRONYMS['vals']
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
  if is_correct and abbrev in gene_to_full_name:
    full_gene_name = gene_to_full_name[abbrev];
    ld = levenshtein.levenshtein(full_gene_name.lower(), ' '.join(definition).lower())
    if float(ld) \
          / len(' '.join(definition)) <= SR['levenshtein_cutoff']:
      is_correct = False
      supertype = 'FALSE_ABBREV_GENE_NAME'
      subtype = full_gene_name + '; LD=' + str(ld)
  if is_correct and len(definition) == 1 and definition[0] in gene_to_full_name:
    is_correct = False
    supertype = 'FALSE_DEFINITION_GENE_NAME'
    subtype = None
  if is_correct and abbrev in SR['short_words']:
    is_correct = False
    supertype = 'FALSE_SHORT_WORD'
    subtype = None
  m = Mention(None, row.doc_id, row.section_id,
              row.sent_id, [i for i in xrange(start_abbrev, stop_abbrev + 1)],
              [i for i in xrange(start_definition, stop_definition + 1)],
              mid, supertype, subtype, abbrev, definition, is_correct);
  return m

def read_gene_to_full_name():
  rv = {}
  with open(onto_path('data/gene_names.tsv')) as f:
    for line in f:
      parts = line.split('\t')
      assert len(parts) == 2, parts
      geneAbbrev = parts[0].strip()
      geneFullName = parts[1].strip()
      ':type geneFullName: str'
      geneFullName = geneFullName.replace('(', '-LRB-')
      geneFullName = geneFullName.replace(')', '-RRB-')
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
