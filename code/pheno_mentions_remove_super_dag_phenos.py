#!/usr/bin/env python
import collections
import os
import sys

import abbreviations
import config
import extractor_util as util
import levenshtein
from data_util as dutil


CACHE = dict()  # Cache results of disk I/O

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('ids', 'int[]'),
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('wordidxs', 'int[]'),
          ('mention_ids', 'text[]'),
          ('supertypes', 'text[]'),
          ('subtypes', 'text[]'),
          ('entities', 'text[]'),
          ('words', 'text[]'),
          ('is_corrects', 'boolean[]'),])

# This defines the output Mention object
Mention = collections.namedtuple('Mention', [
            'dd_id',
            'doc_id',
            'section_id',
            'sent_id',
            'wordidxs',
            'mention_id',
            'supertype',
            'subtype',
            'entity',
            'words',
            'is_correct'])

hpo_dag = dutil.read_hpo_dag()
def pheno_is_child_of(child_entity, parent_entity):
  child_parent_ids = dutil.get_parents(child_entity, hpo_dag)
  return parent_entity in child_parent_ids

def filter_phenos(row):
  doc_id = None
  section_id = None
  sent_id = None
  wordidxs = None
  words = None
  cands = []
  for i, mention_id in enumerate(row.mention_ids):
    ident = ids[i]
    if doc_id is None:
      doc_id = row.doc_id
    assert doc_id == row.doc_id
    if section_id is None:
      section_id = row.section_id
    assert section_id == row.section_id
    if sent_id is None:
      sent_id = row.sent_id
    assert sent_id == row.sent_id
    if wordidxs is None:
      wordidxs = row.wordidxs
    assert wordidxs == row.wordidxs
    if words is None:
      words = row.words
    assert words == row.words

    supertype = row.supertypes[i]
    subtype = row.subtypes[i]
    entity = row.entities[i]
    is_correct = row.is_corrects[i]
    
    current_pheno = Mention(None, doc_id, section_id, sent_id, wordidxs, supertype, subtype, entity, words, is_correct)

    for i in xrange(len(cands)):
      cand = cands[i]
      if pheno_is_child_of(cand.entity, current_pheno.entity):
        break
      if pheno_is_child_of(current_pheno.entity, cand.entity):
        cands[i] = current_pheno
        break

    return cands

if __name__ == '__main__':
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    # Find candidate mentions & supervise
    mentions = filter_phenos(row)

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
