#!/usr/bin/env python
import collections
import extractor_util as util
import random
import re
import os
import sys

CACHE = dict()  # Cache results of disk I/O


def read_phrase_to_genes():
  """Read in phrase to gene mappings. The format is TSV: <Phrase> <EnsemblGeneId> <MappingType>
  
  <MappingType> is one of:
    - OFFICIAL_GENE_SYMBOL
    - GENE_SYMBOL_SYNONYM
    - REFSEQ_ID
    - ENSEMBL_GENE_ID
  """
  with open('%s/onto/data/phrase_to_ensembl.tsv' % util.APP_HOME) as f:
    phrase_to_genes = collections.defaultdict(set)
    lower_phrase_to_genes = collections.defaultdict(set)
    for line in f:
      phrase,ensembl_id,mapping_type = line.rstrip('\n').split('\t')
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


def parse_input_row(line):
  tokens = line.split('\t')
  return util.Sentence(doc_id=tokens[0],
                       sent_id=int(tokens[1]),
                       words=util.tsv_string_to_list(tokens[2]),
                       lemmas=util.tsv_string_to_list(tokens[3]),
                       poses=util.tsv_string_to_list(tokens[4]),
                       ners=util.tsv_string_to_list(tokens[5]))


def get_mentions_for_row(row):
  phrase_to_genes = CACHE['phrase_to_genes']
  lower_phrase_to_genes = CACHE['lower_phrase_to_genes']
  mentions = []
  
  for i, word in enumerate(row.words):
    if word in phrase_to_genes or word.lower() in lower_phrase_to_genes:
      # Treat lowercase mappings the same as exact case ones for now.
      exact_case_matches = phrase_to_genes[word]
      lowercase_matches = phrase_to_genes[word.lower()]
      for ensembl_id,mapping_type in exact_case_matches.union(lowercase_matches):
        mentions.append(util.create_mention(row, [i], [word], ensembl_id, mapping_type))
    elif word == word.upper() and word.isalnum() and not unicode(word).isnumeric() and len(word) > 2:
      if random.random() < 0.05:
        mentions.append(util.create_mention(row, [i], [word], 'ALL_UPPERCASE_NOT_GENE_SYMBOL', 'ALL_UPPERCASE_NOT_GENE_SYMBOL'))
    elif random.random() < 0.0001:
        mentions.append(util.create_mention(row, [i], [word], 'RANDOM_WORD_NOT_GENE_SYMBOL', 'RANDOM_WORD_NOT_GENE_SYMBOL'))

  return mentions


def get_supervision(row, mention):
  """Applies distant supervision rules."""
  word = mention.words[0]
  word_lower = word.lower()
  wordidx = mention.wordidxs[0]

  # Negative Rule #1: words that are all uppercase but are not in the gene symbol
  # list are likely false mentions.
  if mention.mention_type in ('ALL_UPPERCASE_NOT_GENE_SYMBOL', 'RANDOM_WORD_NOT_GENE_SYMBOL'):
    return False

  # Positive Rule #1: matches from papers that NCBI annotates as being about
  # the mentioned gene are likely true.
  pubmed_to_genes = CACHE['pubmed_to_genes']
  pmid = util.get_pubmed_id_for_doc(row.doc_id)
  if pmid:
    mention_ensembl_id = mention.entity.split(":")[0]
    if mention_ensembl_id in pubmed_to_genes.get(pmid, {}):
      return True

  # Default to no supervision
  return None


def create_supervised(row, mention):
  is_correct = get_supervision(row, mention)
  return mention._replace(is_correct=is_correct)


def main():
  CACHE['phrase_to_genes'],CACHE['lower_phrase_to_genes'] = read_phrase_to_genes()
  CACHE['pubmed_to_genes'] = read_pubmed_to_genes()
  mentions = []
  for line in sys.stdin:
    row = parse_input_row(line)
    new_mentions = get_mentions_for_row(row)
    supervised_mentions = [create_supervised(row, m) for m in new_mentions]
    mentions.extend(supervised_mentions)
  for mention in mentions:
    util.print_tsv_output(mention)


if __name__ == '__main__':
  main()
