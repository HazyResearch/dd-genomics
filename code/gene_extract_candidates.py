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
  for i, word in enumerate(row.words):
    
    # Make a template mention object- will have mention_id opt with entity (ensemble_id) appended
    mid = '%s_%s_%s' % (row.doc_id, row.sent_id, i)
    m = Mention(dd_id=None, doc_id=row.doc_id, sent_id=row.sent_id, wordidxs=[i], mention_id=mid, mention_type=None, entity=None, words=[word], is_correct=None)

    # Treat lowercase mappings the same as exact case ones for now.
    # HACK[MORGAN]: Do not learn any 2-letter words
    if (word in phrase_to_genes or word.lower() in lower_phrase_to_genes) and (len(word)>2):
      exact_case_matches = phrase_to_genes[word]
      lowercase_matches = phrase_to_genes[word.lower()]
      for eid, mapping_type in exact_case_matches.union(lowercase_matches):
        mentions.append(
          m._replace(mention_id=mid+'_'+eid, entity=eid, mention_type=mapping_type))
  return mentions


def get_supervision_for_mention(row, mention):
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
      return True, 'NCBI_ANNOTATION_TRUE'

  # Negative Rule #1: "GENE cells / cell lines"
  RGX_CELL_LINES = r'\+?\s*cell(s|\slines?)'
  phrase_post = ' '.join(row.words[wordidx+1:])
  if re.match(RGX_CELL_LINES, phrase_post, flags=re.I):
    return False, 'CELL_LINES'

  # Positive Rule #2: Genes on the gene list with complicated names (3 letters
  # and 1 digit) are probably good for exact matches.
  """
  if mention.mention_type in ('CANONICAL_SYMBOL','NONCANONICAL_SYMBOL'):
    if re.match(r'[a-zA-Z]{3}[a-zA-Z]*\d+\w*', word):
      return True
  """

  # Default to existing supervision
  return mention.is_correct, mention.mention_type


def get_negative_mentions(row, mentions, d, per_row_max=2):
  """Generate random / pseudo-random negative examples, trying to keep set approx. balanced"""
  negs = []
  if d < 0:
    return negs
  existing_mention_idxs = [m.wordidxs[0] for m in mentions]
  for i, word in enumerate(row.words):
    if len(negs) > d or len(negs) > per_row_max:
      return negs

    # skip if an existing mention
    if i in existing_mention_idxs:
      continue
    
    # Make a template mention object- will have mention_id opt with entity (ensemble_id) appended
    mid = '%s_%s_%s' % (row.doc_id, row.sent_id, i)
    m = Mention(dd_id=None, doc_id=row.doc_id, sent_id=row.sent_id, wordidxs=[i], mention_id=mid, mention_type=None, entity=None, words=[word], is_correct=None)

    # Non-match all uppercase negative supervision
    if word==word.upper() and len(word)>2 and word.isalnum() and not unicode(word).isnumeric():
      if random.random() < 0.01*d:
        negs.append(m._replace(mention_type='ALL_UPPER_NOT_GENE_SYMBOL', is_correct=False))

    # Random negative supervision
    elif random.random() < 0.005*d:
      negs.append(m._replace(mention_type='RAND_WORD_NOT_GENE_SYMBOL', is_correct=False))
  return negs


def get_supervised_mentions_for_row(row):
  supervised_mentions = []
  for mention in get_mentions_for_row(row):
    is_correct, mention_type = get_supervision_for_mention(row, mention)
    supervised_mentions.append(mention._replace(is_correct=is_correct, mention_type=mention_type))
  return supervised_mentions


if __name__ == '__main__':

  # load static data
  CACHE['phrase_to_genes'],CACHE['lower_phrase_to_genes'] = read_phrase_to_genes()
  CACHE['pubmed_to_genes'] = read_pubmed_to_genes()
  CACHE['doi_to_pmid'] = dutil.read_doi_to_pmid()
  
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
      mentions = get_supervised_mentions_for_row(row)
    except IndexError:
      util.print_error("Error with row: %s" % (row,))
      continue

    pos_count += len([m for m in mentions if m.is_correct])
    neg_count += len([m for m in mentions if m.is_correct is False])

    # add negative supervision
    if pos_count > neg_count:
      negs = get_negative_mentions(row, mentions, pos_count - neg_count)
      neg_count += len(negs)
      mentions += negs

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
