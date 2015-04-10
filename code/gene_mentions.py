#!/usr/bin/env python
import collections
import extractor_util as util
import os
import sys

CODE_DIR = os.path.dirname(os.path.realpath(__file__))
APP_HOME = os.path.dirname(CODE_DIR)

CACHE = dict()  # Cache results of disk I/O

Row = collections.namedtuple(
    'Row', ['doc_id', 'sent_id', 'words', 'lemmas', 'poses', 'ners'])
Mention = collections.namedtuple(
    'Mention', ['doc_id', 'sent_id', 'wordidxs', 'mention_id', 'mention_type',
                'entity', 'words', 'is_correct'])


def read_genes():
  """Read in lists of gene names and synonyms."""
  all_names = set()
  all_synonyms = dict()
  with open('%s/onto/data/genes.tsv' % APP_HOME) as f:
    for line in f:
      name, synonyms, full_names = line.strip(' \r\n').split('\t')
      # TODO: make use of full_names?  Currently ignored.
      synonyms = set(synonyms.split('|'))
      all_names.add(name)
      for syn in synonyms:
        all_synonyms[syn] = name
  # Lower-case versions of names and synonyms
  all_names_lower = {x.lower(): x for x in all_names}
  all_synonyms_lower = {x.lower(): all_synonyms[x] for x in all_synonyms}
  return (all_names, all_names_lower, all_synonyms, all_synonyms_lower)


def read_bad_genes():
  """Read in a list of gene names/synonyms that are problematic."""
  with open('%s/onto/manual/gene_english.tsv' % APP_HOME) as f:
    # Genes that are also English words
    gene_english = set([x.strip().lower() for x in f])
  with open('%s/onto/manual/gene_bigrams.tsv' % APP_HOME) as f:
    # Two-letter gene names
    gene_bigrams = set([x.strip().lower() for x in f])
  with open('%s/onto/manual/gene_noisy.tsv' % APP_HOME) as f:
    # Other problematic genes
    gene_noisy = set([x.strip().lower() for x in f])
  bad_genes = gene_english | gene_bigrams | gene_noisy
  return bad_genes


def parse_input_row(line):
  tokens = line.split('\t')
  return Row(doc_id=tokens[0],
             sent_id=int(tokens[1]),
             words=util.tsv_string_to_list(tokens[2]),
             lemmas=util.tsv_string_to_list(tokens[3]),
             poses=util.tsv_string_to_list(tokens[4]),
             ners=util.tsv_string_to_list(tokens[5]))


def get_supervision(row, wordidx, mention_type, entity, word):
  """Applies distant supervision rules."""
  # Two-letter capital words
  if len(word) == 2 and word.isupper() and word.isalpha():
    has_pub_date = 'DATE' in row.ners and 'NUMBER' in row.ners
    # is or right next to a person/organization word
    for j in range(max(0, wordidx - 1), min(wordidx + 2, len(row.words))):
      if has_pub_date and row.ners[j] in ('PERSON', 'ORGANIZATION'):
        return False
    else:
      return None
  return True


def create_mention(row, wordidx, mention_type, entity, word):
    """Create a mention record."""
    mention_id = '%s_%s_%d_1' % (row.doc_id, row.sent_id, wordidx)
    is_correct = get_supervision(row, wordidx, mention_type, entity, word)
    mention = Mention(doc_id=row.doc_id, 
                      sent_id=row.sent_id,
                      wordidxs=[wordidx],
                      mention_id=mention_id,
                      mention_type=mention_type, 
                      entity=entity,
                      words=[word],
                      is_correct=is_correct)
    return mention


def get_mentions_for_row(row):
  gene_names, gene_names_lower, gene_synonyms, gene_synonyms_lower = CACHE['genes']
  bad_gene_names = CACHE['bad_genes']
  mentions = []
  for i, word in enumerate(row.words):
    if len(word) == 1: continue
    word_lower = word.lower()
    mention = None
    if word in gene_names:
      mention = create_mention(row, i, 'NAME', word, word)
    elif word in gene_synonyms:
      mention = create_mention(row, i, 'SYN', word, gene_synonyms[word])
    elif word_lower in bad_gene_names:
      # forbid non-case-exact matches for these genes
      continue
    elif word_lower in gene_names_lower:
      mention = create_mention(row, i, 'NAME_LOWER', word,
                               gene_names_lower[word_lower])
    elif word_lower in gene_synonyms_lower:
      mention = create_mention(row, i, 'SYN_LOWER', word,
                               gene_synonyms_lower[word_lower])
    if mention:
      mentions.append(mention)
  #if mentions:
  #  print >> sys.stderr, 'Sentence: %s' % ' '.join(row.words)
  #  for mention in mentions:
  #    print >> sys.stderr, '  Mention: (%s)' % ', '.join(str(x) for x in mention)
  return mentions


def main():
  CACHE['genes'] = read_genes()
  CACHE['bad_genes'] = read_bad_genes()
  mentions = []
  for line in sys.stdin:
    mentions.extend(get_mentions_for_row(parse_input_row(line)))
  for mention in mentions:
    util.print_tsv_output(mention)


if __name__ == '__main__':
  main()
