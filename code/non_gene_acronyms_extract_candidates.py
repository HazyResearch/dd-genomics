#!/usr/bin/env python
import collections
import os
import sys

import abbreviations
import config
import extractor_util as util
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
          ('ners', 'text[]'),
          ('gene_wordidx_array', 'int[]')])


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

def contains_sublist(lst, sublst):
  if len(sublst) < len(lst):
    return False, None
  n = len(sublst)
  for i in xrange(len(lst) - n + 1):
    if i+n <= len(lst):
      if sublst == lst[i:i+n]:
        return True, (i,i+n)
  return False

def detect_manual(words, gene_idx):
  gene_name = words[gene_idx]
  manual_pairs = SR['manual-pairs']
  if gene_name in manual_pairs:
    for definition in manual_pairs[gene_name]:
      def_lst = definition.split()
      contains, def_boundaries = contains_sublist(words, def_lst)
      if contains:
        def_start, def_stop = def_boundaries
        definition = words[def_start:def_stop]
        abbrev = gene_name
        abbrev_start = gene_idx
        abbrev_stop = gene_idx + 1
        return contains, (abbrev_start, abbrev_stop, abbrev), (def_start, def_stop, definition), 'MANUAL'
  return False, None, None, None

def extract_candidate_mentions(row, pos_count, neg_count):
  mentions = []
  found = False
  if abbreviations.conditions(row.words[row.gene_wordidx]):
    for (is_correct, abbrev, definition, detector_message) in abbreviations.getabbreviations(row.words, abbrev_index=row.gene_wordidx):
      m = create_supervised_mention(row, is_correct, abbrev, definition, detector_message, pos_count, neg_count)
      if m:
        mentions.append(m)
        found = True
  if not found:
    is_correct, abbrev, definition, detector_message = detect_manual(row.words, abbrev_index=row.gene_wordidx)
    if is_correct:
      m = create_supervised_mention(row, is_correct, abbrev, definition, detector_message, pos_count, neg_count)
      if m:
        mentions.append(m)
        found = True
  return mentions

### DISTANT SUPERVISION ###
VALS = config.NON_GENE_ACRONYMS['vals']
def create_supervised_mention(row, is_correct, 
                              (start_abbrev, stop_abbrev, abbrev), 
                              (start_definition, stop_definition, 
                               definition), detector_message, pos_count,
                               neg_count):
  assert stop_abbrev == start_abbrev + 1
  mid = '%s_%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id, start_abbrev)
  gene_to_full_name = CACHE['gene_to_full_name']
  include = None
  if is_correct:
    supertype = 'TRUE_DETECTOR'
    subtype = None
  elif is_correct is False:
    supertype = 'FALSE_DETECTOR'
    subtype = detector_message
  else:
    supertype = 'DETECTOR_OMITTED_SENTENCE'
    subtype = None
    include = False
    # print >>sys.stderr, supertype
  if is_correct and include is not False:
    if abbrev in gene_to_full_name:
      full_gene_name = gene_to_full_name[abbrev]
      ld = levenshtein.levenshtein(full_gene_name.lower(), ' '.join(definition).lower())
      fgl = len(full_gene_name)
      dl = len(' '.join(definition))
      if dl >= fgl*0.75 and dl <= fgl*1.25 and float(ld) \
            / len(' '.join(definition)) <= SR['levenshtein_cutoff']:
        is_correct = False
        supertype = 'FALSE_DEFINITION_IS_GENE_FULL'
        # print >>sys.stderr, supertype
        subtype = full_gene_name + '; LD=' + str(ld)
        include = False
  if include is not False and is_correct and len(definition) == 1 and definition[0] in gene_to_full_name:
    is_correct = False
    supertype = 'FALSE_DEFINITION_IS_GENE_ABBREV'
    # print >>sys.stderr, supertype
    subtype = None
  if include is not False and is_correct and abbrev in SR['short-words']:
    is_correct = False
    supertype = 'FALSE_SHORT_WORD'
    # print >>sys.stderr, supertype
    subtype = None
  # print >>sys.stderr, (include, is_correct, neg_count, pos_count)
  if include is True or (include is not False and is_correct is True or (is_correct is False and neg_count < pos_count)):
    m = Mention(None, row.doc_id, row.section_id,
              row.sent_id, [i for i in xrange(start_abbrev, stop_abbrev + 1)],
              [i for i in xrange(start_definition, stop_definition + 1)],
              mid, supertype, subtype, abbrev, definition, is_correct);
  else:
    m = None
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

    #Specific to ddlog, add two conditions that are not possible directly in the sql query.
    row.gene_wordidx = row.gene_wordidx_array[0]
    # print >> sys.stderr, 'patate'
    # print >> sys.stderr, row
    if '-LRB-' not in row.words[row.gene_wordidx - 1]:
      continue

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
