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

CACHE = dict()  # Cache results of disk I/O


# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text'),
          ('poses', 'text'),
          ('dep_paths', 'text'),
          ('dep_parents', 'text'),
          ('gene_wordidxs', 'int[][]'),
          ('gene_supertypes', 'text[]'),
          ('pheno_wordidxs', 'int[][]'),
          ('pheno_supertypes', 'text[]')])


# This defines the output Mention object
Mention = collections.namedtuple('Mention', [
            'doc_id',
            'section_id',
            'sent_id',
            'words',
            'lemmas',
            'poses',
            'ners',
            'dep_paths',
            'dep_parents'])

def create_ners(row):
    m = Mention(row.doc_id, row.section_id, row.sent_id, '|^|'.join(row.words), \
                row.lemmas, row.poses, None, row.dep_paths, \
                row.dep_parents)
    ners = ['O' for _ in xrange(len(row.words))]
    #print >>sys.stderr, (str(row.gene_wordidxs), str(row.gene_supertypes), \
    #                     str(row.pheno_wordidxs), str(row.pheno_supertypes))
    for i, wordidxs in enumerate(row.pheno_wordidxs):
      pheno_supertype = row.pheno_supertypes[i]
      if re.match('RAND_NEG', pheno_supertype) or re.match('BAD', pheno_supertype) or pheno_supertype == 'O':
        continue
      ners[wordidxs[0]] = 'PHENO'
    for i, wordidxs in enumerate(row.gene_wordidxs):
      gene_supertype = row.gene_supertypes[i]
      if gene_supertype == 'BAD_GENE' or gene_supertype == 'MANUAL_BAD' or gene_supertype == 'RAND_WORD_NOT_GENE_SYMBOL' \
          or gene_supertype == 'ABBREVIATION' or gene_supertype == 'ALL_UPPER_NOT_GENE_SYMBOL' or gene_supertype == 'O':
        continue
      ners[wordidxs[0]] = 'GENE'
    return m._replace(ners='|^|'.join(ners))

if __name__ == '__main__':
  # generate the mentions, while trying to keep the supervision approx. balanced
  # print out right away so we don't bloat memory...
  pos_count = 0
  neg_count = 0
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    out_row = create_ners(row)
    util.print_tsv_output(out_row)
