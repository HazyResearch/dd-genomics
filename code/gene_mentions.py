#!/usr/bin/env python
import collections
import extractor_util as util
import re
import os
import sys

CACHE = dict()  # Cache results of disk I/O

Row = collections.namedtuple(
    'Row', ['doc_id', 'sent_id', 'words', 'lemmas', 'poses', 'ners'])


def read_genes():
  """Read in lists of gene names and synonyms."""
  all_names = set()
  all_synonyms = dict()
  with open('%s/onto/data/genes.tsv' % util.APP_HOME) as f:
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
  with open('%s/onto/manual/gene_english.tsv' % util.APP_HOME) as f:
    # Genes that are also English words
    gene_english = set([x.strip().lower() for x in f])
  with open('%s/onto/manual/gene_bigrams.tsv' % util.APP_HOME) as f:
    # Two-letter gene names
    gene_bigrams = set([x.strip().lower() for x in f])
  bad_genes = gene_english | gene_bigrams
  return bad_genes


def read_misc_noisy_genes():
  """Read Feng's manually compiled list of weird gene names
  
  It's not scalable to use a list like this for actual extraction, but this
  is a good source of supervision.
  """
  with open('%s/onto/manual/gene_noisy.tsv' % util.APP_HOME) as f:
    # Other problematic genes
    gene_noisy = set([x.strip().lower() for x in f])
  return gene_noisy


def parse_input_row(line):
  tokens = line.split('\t')
  return Row(doc_id=tokens[0],
             sent_id=int(tokens[1]),
             words=util.tsv_string_to_list(tokens[2]),
             lemmas=util.tsv_string_to_list(tokens[3]),
             poses=util.tsv_string_to_list(tokens[4]),
             ners=util.tsv_string_to_list(tokens[5]))


def create_mention(row, wordidx, mention_type, entity, word):
    """Create a mention record."""
    mention_id = '%s_%s_%d_1' % (row.doc_id, row.sent_id, wordidx)
    mention = util.Mention(db_id='\N',  # leave id field blank
                           doc_id=row.doc_id, 
                           sent_id=row.sent_id,
                           wordidxs=[wordidx],
                           mention_id=mention_id,
                           mention_type=mention_type, 
                           entity=entity,
                           words=[word],
                           is_correct=None)
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
      mention = create_mention(row, i, 'SYN', gene_synonyms[word], word)
    elif word_lower in bad_gene_names:
      # forbid non-case-exact matches for these genes
      continue
    elif word_lower in gene_names_lower:
      mention = create_mention(row, i, 'NAME_LOWER',
                               gene_names_lower[word_lower], word)
    elif word_lower in gene_synonyms_lower:
      mention = create_mention(row, i, 'SYN_LOWER',
                               gene_synonyms_lower[word_lower], word)
    if mention:
      mentions.append(mention)
  return mentions


def get_supervision(row, mention):
  """Applies distant supervision rules."""
  word = mention.words[0]
  word_lower = word.lower()
  wordidx = mention.wordidxs[0]
  print ' '.join(row.words)
  print word_lower


  # Gene names that are ambiguous
  bad_genes = CACHE['bad_genes']  # English words and 2-letter abbreviations
  misc_noisy_genes = CACHE['misc_noisy_genes']  # Feng's manual list of problem genes
  sentence_all_upper = all(not x.isalpha() or x.isupper() for x in row.words)
  print sentence_all_upper
  if sentence_all_upper or mention.mention_type in ('NAME_LOWER', 'SYN_LOWER'):
    # Sentence is entirely uppercase, or match is not exact case match
    if word_lower in bad_genes or word_lower in misc_noisy_genes:
      return False

  # NER tag: word is or is next to a person/organization/location/date
  for j in range(max(0, wordidx - 1), min(wordidx + 2, len(row.words))):
    if row.ners[j] in ('PERSON', 'ORGANIZATION', 'LOCATION', 'DATE'):
      return False

  # Genes with complicated names are probably good for exact matches.
  # Here, require at least 4 letters and 1 digit.
  if mention.mention_type in ('NAME', 'SYN'):
    # An exact case match
    if re.match(r'[a-zA-Z]{3}[a-zA-Z]*[0-9]+', word):
      return True

  # Default to no supervision
  return None


def create_supervised(row, mention):
  is_correct = get_supervision(row, mention)
  return mention._replace(is_correct=is_correct)


def main():
  CACHE['genes'] = read_genes()
  CACHE['bad_genes'] = read_bad_genes()
  CACHE['misc_noisy_genes'] = read_misc_noisy_genes()
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
