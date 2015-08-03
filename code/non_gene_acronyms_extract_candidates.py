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
            'entity',
            'words',
            'is_correct'])

### CANDIDATE EXTRACTION ###
HF = config.GENE['HF']
SR = config.GENE['SR']


def extract_candidate_mentions(row, pos_count, neg_count):
  phrase_to_genes = CACHE['phrase_to_genes']
  lower_phrase_to_genes = CACHE['lower_phrase_to_genes']
  mentions = []
  for i, word in enumerate(row.words):
    if word == '-LRB-':
      ...
      m = create_supervised_mention(row, i, eid, mapping_type)
  return mentions
  return mentions

 
### DISTANT SUPERVISION ###
VALS = config.PHENO_ACRONYMS['vals']
def create_supervised_mention(row, i, entity=None, mention_supertype=None, mention_subtype=None):
  """Given a Row object consisting of a sentence, create & supervise a Mention output object"""
  word = row.words[i]
  word_lower = word.lower()
  mid = '%s_%s_%s_%s_%s_%s' % (row.doc_id, row.section_id, row.sent_id, i, entity, mention_supertype)
  m = Mention(None, row.doc_id, row.section_id, row.sent_id, [i], mid, mention_supertype, mention_subtype, entity, [word], None)
  dep_dag = deps.DepPathDAG(row.dep_parents, row.dep_paths, row.words)

  if SR.get('post-match'):
    opts = SR['post-match']
    phrase_post = " ".join(row.words[i+1:])
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(phrase_post, opts[name], opts['%s-rgx' % name], flags=re.I)
        if match:
          return m._replace(is_correct=val, mention_supertype='POST_MATCH_%s_%s' % (name, val), mention_subtype=match)

  if SR.get('pre-neighbor-match') and i > 0:
    opts = SR['pre-neighbor-match']
    pre_neighbor = row.words[i-1]
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(pre_neighbor, opts[name], opts['%s-rgx' % name], flags=re.I)
        if match:
          return m._replace(is_correct=val, mention_supertype='PRE_NEIGHBOR_MATCH_%s_%s' % (name, val), mention_subtype=match)

  ## DS RULE: matches from papers that NCBI annotates as being about the mentioned gene are likely true.
  if SR['pubmed-paper-genes-true']:
    pubmed_to_genes = CACHE['pubmed_to_genes']
    pmid = dutil.get_pubmed_id_for_doc(row.doc_id)
    if pmid and entity:
      mention_ensembl_id = entity.split(":")[0]
      if mention_ensembl_id in pubmed_to_genes.get(pmid, {}):
        return m._replace(is_correct=True, mention_supertype='%s_NCBI_ANNOTATION_TRUE' % mention_supertype, mention_subtype=mention_ensembl_id)

  ## DS RULE: Genes on the gene list with complicated names are probably good for exact matches.
  if SR['complicated-gene-names-true']:
    if mention.mention_supertype in ('CANONICAL_SYMBOL','NONCANONICAL_SYMBOL'):
      if re.match(r'[a-zA-Z]{3}[a-zA-Z]*\d+\w*', word):
        return m._replace(is_correct=True, mention_supertype='COMPLICATED_GENE_NAME')

  if SR.get('neighbor-match'):
    opts = SR['neighbor-match']
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        for neighbor_idx in dep_dag.neighbors(i):
          neighbor = row.words[neighbor_idx]
          match = util.rgx_mult_search(neighbor, opts[name],  opts['%s-rgx' % name], flags=re.I)
          if match:
            return m._replace(is_correct=val, mention_supertype='NEIGHBOR_MATCH_%s_%s' % (name, val), mention_subtype='Neighbor: ' + neighbor + ', match: ' + match)

  return m


if __name__ == '__main__':
  # load static data
  CACHE['gene_to_full_name'] = read_gene_to_full_name()
  CACHE['pheno_full_names'] = read_pheno_full_names()
  
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
