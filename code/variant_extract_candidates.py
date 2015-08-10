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

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]')])

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
            'entity',
            'words',
            'is_correct'])

### CANDIDATE EXTRACTION ###
HF = config.GENEVAR['HF']

### GENE-VARIANT ###

# regexes from tmVar paper
# See Table 3 in http://bioinformatics.oxfordjournals.org/content/early/2013/04/04/bioinformatics.btt156.full.pdf
def comp_gv_rgx():
  
  # A bit silly, but copy from pdf wasn't working, and this format is simple to copy & debug...
  a = r'[cgrm]'
  i = r'IVS'
  b = r'ATCGatcgu'

  s1 = r'0-9\_\.\:'
  s2 = r'\/\>\?\(\)\[\]\;\:\*\_\-\+0-9'
  s3 = r'\/\>\<\?\(\)\[\]\;\:\*\_\-\+0-9'

  b1 = r'[%s]' % b
  bs1 = r'[%s%s]' % (b,s1)
  bs2 = r'[%s %s]' % (b,s2)
  bs3 = r'[%s %s]' % (b,s3)

  c1 = r'(inv|del|ins|dup|tri|qua|con|delins|indel)'
  c2 = r'(del|ins|dup|tri|qua|con|delins|indel)'
  c3 = r'(inv|del|ins|dup|tri|qua|con|delins|indel|fsX|fsx|fs)'

  p = r'CISQMNPKDTFAGHLRWVEYX'
  ps2 = r'[%s %s]' % (p, s2)
  ps3 = r'[%s %s]' % (p, s3)

  # regexes correspond to gene ('g') or protein ('p') variants
  GV_RGXS = [
    (r'(%s\.%s+%s%s*)' % (a,bs3,c1,bs1), 'g'),
    (r'(IVS%s+%s%s*)' % (bs3,c2,bs1), 'g'),
    (r'((%s\.|%s)%s+)' % (a,i,bs2), 'g'),
    (r'((%s\.)?%s[0-9]+%s)' % (a,b1,b1), 'g'),
    (r'([0-9]+%s%s*)' % (c2,b1), 'g'),
    (r'([p]\.%s+%s%s*)' % (ps3,c3,ps3), 'p'),
    (r'([p]\.%s+)' % ps2, 'p'),
    (r'([p]\.[A-Z][a-z]{0,2}[\W\-]{0,1}[0-9]+[\W\-]{0,1}([A-Z][a-z]{0,2}|(fs|fsx|fsX)))', 'p')]

  # Just return as one giant regex for now
  return r'|'.join([gvr[0] for gvr in GV_RGXS])

def extract_candidate_mentions(row, gv_rgx):
  mentions = []
  for i,word in enumerate(row.words):
    if re.match(gv_rgx, word, flags=re.I):
      mentions.append(Mention(
        dd_id=None, 
        doc_id=row.doc_id, 
        section_id=row.section_id,
        sent_id=row.sent_id,
        wordidxs=[i],
        mention_id='%s_%s_%s_%s_GV' % (row.doc_id, row.section_id, row.sent_id, i),
        mention_supertype='GV_RGX_MATCH',
        mention_subtype=None,
        entity=word,
        words=[word],
        is_correct=True))

    # Sometimes some of the regex patterns get split up
    elif re.match(r'[cgrm]\.|IVS.*', word):
      for j in range(i+1, min(i+7, len(row.words))):
        words = row.words[i:j]
        if re.match(gv_rgx, ''.join(words), flags=re.I):
          mentions.append(Mention(
            dd_id=None, 
            doc_id=row.doc_id, 
            section_id=row.section_id,
            sent_id=row.sent_id,
            wordidxs=range(i,j),
            mention_id='%s_%s_%s_%s_%s_GV' % (row.doc_id, row.section_id, row.sent_id, i, j),
            mention_supertype='GV_RGX_MATCH',
            mention_subtype=None,
            entity=''.join(words),
            words=words,
            is_correct=True))
          break
  return mentions


if __name__ == '__main__':
  GV_RGX = r'^(%s)$' % comp_gv_rgx()
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    # Skip row if sentence doesn't contain a verb, contains URL, etc.
    if util.skip_row(row):
      continue

    # Find candidate mentions & supervise
    #try:
    mentions = extract_candidate_mentions(row, GV_RGX)
    #except IndexError:
    #  util.print_error("Error with row: %s" % (row,))
    #  continue

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
