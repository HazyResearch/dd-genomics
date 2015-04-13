#!/usr/bin/env python
from collections import namedtuple, defaultdict
import sys
import re
import os
GDD_HOME = os.environ['GDD_HOME']

# TODO: delete these and get from robin's util file post-merge
# TODO: add in tuple type to Robin's code!
def list_to_pg_array(l):
  """Convert a list to a string that PostgreSQL's COPY FROM understands."""
  return '{%s}' % ','.join(str(x) for x in l)

def print_tsv_output(out_record):
  """Print a tuple as output of TSV extractor."""
  values = []
  for x in out_record:
    if isinstance(x, list) or isinstance(x, tuple):
      cur_val = list_to_pg_array(x)
    elif x is None:
      cur_val = '\N'
    else:
      cur_val = x
    values.append(cur_val)
  print '\t'.join(str(x) for x in values)

Sentence = namedtuple('Sentence', ['doc_id', 'sent_id', 'words', 'poses', 'ners', 'lemmas'])
Mention = namedtuple('Mention', ['dd_id', 'doc_id', 'sent_id', 'wordidxs', 'mention_id', 'mention_type', 'entity', 'words', 'is_correct'])

# Load stop words list
# [See onto/gen_basic_stopwords.py]
STOPWORDS = frozenset([w.strip() for w in open('%s/onto/manual/stopwords.tsv' % (GDD_HOME,), 'rb')])

# Load phenotypes
# [See onto/prep_pheno_terms.py]
# NOTE: for now, we don't distinguish between lemmatized / exact
PHENOS = defaultdict(lambda : None)
rows = [line.split('\t') for line in open('%s/onto/data/pheno_terms.tsv' % (GDD_HOME,), 'rb')]
for row in rows:
  PHENOS[row[1].strip()] = row[0].strip()

### CANDIDATE EXTRACTION FUNCTIONS ###
def parse_line(line, array_sep='|^|'):
  """Parses input line from tsv extractor input, with |^|-encoded array format"""
  cols = line.split('\t')
  return Sentence(doc_id=cols[0],
                  sent_id=int(cols[1]),
                  words=cols[2].split(array_sep),
                  poses=cols[3].split(array_sep),
                  ners=cols[4].split(array_sep),
                  lemmas=cols[5].split(array_sep))

def extract_candidates(tokens, s):
  """Extracts candidate phenotype mentions from a (filtered) list of token tuples"""
  if len(tokens) == 0: return []
  candidates = []
  m = Mention(None, s.doc_id, s.sent_id, None, None, None, None, None, None) 

  # get all n-grams (w/ n <= MAX_LEN) and check for exact or exact lemma match
  # we go through n in descending order to prefer the longest possible exact match
  MAX_LEN = 8
  sl = len(tokens)
  for l in reversed(range(1, min(sl, MAX_LEN+1))):
    for start in range(sl-l+1):
      wordidxs, words, lemmas = zip(*tokens[start:(start+l)])
      exact = PHENOS[' '.join(words)]
      entity = exact if exact else PHENOS[' '.join(lemmas)]

      # handle exact / exact lemma matches recursively to exclude overlapping mentions
      # NOTE: this is something we definitely want to think about further!
      if entity:
        mid = '%s_%s_%s_%s' % (s.doc_id, s.sent_id, wordidxs[0], wordidxs[-1]) 
        candidates.append(m._replace(mention_id=mid, wordidxs=wordidxs, entity=entity, words=words))
        return candidates + extract_candidates(tokens[:start], s) + extract_candidates(tokens[start+l:], s)
  return candidates


def extract_candidates_from_line(line):
  """Extracts candidate phenotype mentions from an input line as Sentence object"""
  s = parse_line(line)

  # filter stop words and process recursively as list of token tuple objects
  tokens = [(i, s.words[i].lower(), s.lemmas[i]) for i in range(len(s.words))]
  tokens = filter(lambda t : t[1] not in STOPWORDS and len(t[1]) > 2, tokens)
  if len(tokens) == 0: return []
  return extract_candidates(tokens, s)

### RUN ###
# extract and supervise mention candidates
candidates = []
for line in sys.stdin:
  candidates += extract_candidates_from_line(line)

# print to stdout
for c in candidates:
  print_tsv_output(c)
