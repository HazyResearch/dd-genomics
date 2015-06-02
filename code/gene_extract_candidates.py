#!/usr/bin/env python
import collections
import extractor_util as util
import data_util as dutil
import random
import re
import os
import sys
import string

CACHE = dict()  # Cache results of disk I/O

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]')])

# This defines the output Mention object
Mention = collections.namedtuple('Mention', [
            'dd_id',
            'doc_id',
            'sent_id',
            'wordidxs',
            'mention_id',
            'mention_type',
            'entity',
            'words',
            'is_correct'])

def read_phrase_to_genes():
  """Read in phrase to gene mappings. The format is TSV: <EnsemblGeneId> <Phrase> <MappingType>
  
  <MappingType> is one of:
    - CANONICAL_GENE_SYMBOL
    - NONCANONICAL_GENE_SYMBOL
    - REFSEQ_ID
    - ENSEMBL_ID
  """
  with open('%s/onto/data/ensembl_genes.tsv' % util.APP_HOME) as f:
    phrase_to_genes = collections.defaultdict(set)
    lower_phrase_to_genes = collections.defaultdict(set)
    for line in f:
      ensembl_id,phrase,mapping_type = line.rstrip('\n').split('\t')
      phrase_to_genes[phrase].add((ensembl_id,mapping_type))
      lower_phrase_to_genes[phrase.lower()].add((ensembl_id,mapping_type))
  return phrase_to_genes, lower_phrase_to_genes

def read_pubmed_to_genes():
  """NCBI provides a list of articles (PMIDs) that discuss a particular gene (Entrez IDs).
  These provide a nice positive distant supervision set, as mentions of a gene name in
  an article about that gene are likely to be true mentions.
  
  This returns a dictionary that maps from Pubmed ID to a set of ENSEMBL genes mentioned
  in that article.
  """
  pubmed_to_genes = collections.defaultdict(set)
  with open('%s/onto/data/pmid_to_ensembl.tsv' % util.APP_HOME) as f:
    for line in f:
      pubmed,gene = line.rstrip('\n').split('\t')
      pubmed_to_genes[pubmed].add(gene)
  return pubmed_to_genes


def get_mentions_for_row(row):
  phrase_to_genes = CACHE['phrase_to_genes']
  lower_phrase_to_genes = CACHE['lower_phrase_to_genes']
  mentions = []
  skip_sentence = False

  # Throw out gene candidates whose sentences contain these words or elements of words:
  exclude_list = ['scholar.google.com/scholar', 'http://', 'https://']
  for word in row.words:
    if any(x in word for x in exclude_list): 
      skip_sentence = True

  # Throw out gene candidates whose sentences do not contain a coreNLP-tagged verb     
  if any(x in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] for x in row.poses) and not (skip_sentence): 
    for i, word in enumerate(row.words):
      mid = '%s_%s_%s' % (row.doc_id, row.sent_id, i)
      m = Mention(dd_id=None, doc_id=row.doc_id, sent_id=row.sent_id, wordidxs=[i], mention_id=mid, mention_type=None, entity=None, words=[word], is_correct=None)

      # Treat lowercase mappings the same as exact case ones for now.
      # HACK[MORGAN]
      # Do not learn any 2-letter words
      if (word in phrase_to_genes or word.lower() in lower_phrase_to_genes) and (len(word)>2):
        exact_case_matches = phrase_to_genes[word]
        lowercase_matches = phrase_to_genes[word.lower()]
        for eid, mapping_type in exact_case_matches.union(lowercase_matches):
          mentions.append(m._replace(entity=eid, mention_type=mapping_type))

      # Non-match all uppercase negative supervision
      elif word == word.upper() and len(word) > 2 and word.isalnum() and not unicode(word).isnumeric():
        if random.random() < 0.05:
          mentions.append(m._replace(mention_type='ALL_UPPER_NOT_GENE_SYMBOL', is_correct=False))

      # Random negative supervision
      elif random.random() < 0.002:
        mentions.append(m._replace(mention_type='RAND_WORD_NOT_GENE_SYMBOL', is_correct=False))
  return mentions

def get_supervision(row, mention):
  """Applies additional distant supervision rules."""
  word = mention.words[0]
  word_lower = word.lower()
  wordidx = mention.wordidxs[0]

  # Positive Rule #1: matches from papers that NCBI annotates as being about
  # the mentioned gene are likely true.
  pubmed_to_genes = CACHE['pubmed_to_genes']
  pmid = dutil.get_pubmed_id_for_doc(row.doc_id, doi_to_pmid=CACHE['doi_to_pmid'])
  if pmid and mention.entity:
    mention_ensembl_id = mention.entity.split(":")[0]
    if mention_ensembl_id in pubmed_to_genes.get(pmid, {}):
      return True

  # Positive Rule#2: Genes on the gene list with complicated names (3 letters
  # and 1 digit) are probably good for exact matches.
  """
  if mention.mention_type in ('CANONICAL_SYMBOL','NONCANONICAL_SYMBOL'):
    if re.match(r'[a-zA-Z]{3}[a-zA-Z]*\d+\w*', word):
      return True
  """

  # Default to existing supervision
  return mention.is_correct

def get_supervised_mentions_for_row(row):
  supervised_mentions = []
  for mention in get_mentions_for_row(row):
    is_correct = get_supervision(row, mention)
    supervised_mentions.append(mention._replace(is_correct=is_correct))
  return supervised_mentions

if __name__ == '__main__':
  CACHE['phrase_to_genes'],CACHE['lower_phrase_to_genes'] = read_phrase_to_genes()
  CACHE['pubmed_to_genes'] = read_pubmed_to_genes()
  CACHE['doi_to_pmid'] = dutil.read_doi_to_pmid()
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_supervised_mentions_for_row)
