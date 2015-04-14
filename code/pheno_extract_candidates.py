#!/usr/bin/env python
from collections import defaultdict
import sys
import re
import os
import random
from itertools import chain
from extractor_util import print_tsv_output, create_mention, Sentence, Mention

def parse_line(line, array_sep='|^|'):
  """Parses input line from tsv extractor input, with |^|-encoded array format"""
  cols = line.split('\t')
  return Sentence(doc_id=cols[0],
                  sent_id=int(cols[1]),
                  words=cols[2].split(array_sep),
                  poses=cols[3].split(array_sep),
                  ners=cols[4].split(array_sep),
                  lemmas=cols[5].split(array_sep))

# Load stop words list
# [See onto/gen_basic_stopwords.py]
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)
STOPWORDS = frozenset([w.strip() for w in open(onto_path('manual/stopwords.tsv'), 'rb')])

# Load list of english words
ENGLISH_WORDS = frozenset([w.strip() for w in open(onto_path('data/english_words.tsv'), 'rb')])

# Load phenotypes (as phrases + as frozensets to allow permutations)
# [See onto/prep_pheno_terms.py]
# NOTE: for now, we don't distinguish between lemmatized / exact
PHENOS = defaultdict(lambda : None)
PHENO_SETS = defaultdict(lambda : None)
rows = [line.split('\t') for line in open(onto_path('data/pheno_terms.tsv'), 'rb')]
for row in rows:
  hpoid, phrase, entry_type = [x.strip() for x in row]
  PHENOS[phrase] = hpoid

  # NOTE: do we have to worry about collisions here?  Probably not too big of deal because if there
  # are multiple HPO entries that are permutations of the same set, likely one will exact match...
  PHENO_SETS[frozenset(phrase.split())] = hpoid


### CANDIDATE EXTRACTION + POSITIVE SUPERVISION ###
MAX_LEN = 8
COMMON_WORD_PROB = 0.4
def extract_candidates(tokens, s):
  """Extracts candidate phenotype mentions from a (filtered) list of token tuples"""
  if len(tokens) == 0: return []
  candidates = []

  # get all n-grams (w/ n <= MAX_LEN) and check for exact or exact lemma match
  # we go through n in descending order to prefer the longest possible exact match
  for l in reversed(range(1, min(len(tokens), MAX_LEN+1))):
    for start in range(len(tokens)-l+1):
      wordidxs, words, lemmas = zip(*tokens[start:(start+l)])

      # (1) Check for exact match (including exact match of lemmatized / stop words removed)
      phrase, lemma_phrase = [' '.join(x) for x in (words, lemmas)]
      if PHENOS[phrase] or PHENOS[lemma_phrase]:
        entity = PHENOS[phrase] if PHENOS[phrase] else PHENOS[lemma_phrase]

        # Supervise exact matches as true; however if exact match is also a common english word,
        # label true w.p. < 1
        if len(words) == 1 and phrase in ENGLISH_WORDS:
          is_correct = True if random.random() < COMMON_WORD_PROB else None
        else:
          is_correct = True

        # handle exact / exact lemma matches recursively to exclude overlapping mentions
        candidates.append(create_mention(s, wordidxs, words, entity, 'EXACT', is_correct))
        return candidates + extract_candidates(tokens[:start], s) \
                          + extract_candidates(tokens[start+l:], s)

      # (2) Check for permuted match
      phrase_set, lemma_set = [frozenset(x) for x in (words, lemmas)]
      if PHENO_SETS[phrase_set] or PHENO_SETS[lemma_set]:
        entity = PHENO_SETS[phrase_set] if PHENO_SETS[phrase_set] else PHENO_SETS[lemma_set]
        candidates.append(create_mention(s, wordidxs, words, entity, 'PERM', None))

      # (3) Check for an exact match with one ommitted (interior) word/lemma
      if len(words) > 2:
        for j in range(1,len(words)-1):
          phrase, lemma_phrase = [' '.join([w for i,w in enumerate(x) if i != j]) \
                                    for x in (words, lemmas)]
          if PHENOS[phrase] or PHENOS[lemma_phrase]:
            entity = PHENOS[phrase] if PHENOS[phrase] else PHENOS[lemma_phrase]
            candidates.append(create_mention(s, wordidxs, words, entity, 'OMIT_%s' % (j,), None))
  return candidates

def extract_candidates_from_sentence(s):
  """Extracts candidate phenotype mentions from an input line as Sentence object"""
  tokens = [(i, s.words[i].lower(), s.lemmas[i]) for i in range(len(s.words))]
  tokens = filter(lambda t : t[1] not in STOPWORDS and len(t[1]) > 2, tokens)
  return extract_candidates(tokens, s)


### NEGATIVE SUPERVISION ###
NEG_EX_PROB = 0.005
def negative_supervision(s, candidates):
  """Generate some negative examples"""
  negs = []
  if random.random() > NEG_EX_PROB: return negs
  
  # pick a random noun phrase which does not overlap with candidate mentions
  covered = set(chain.from_iterable([m.wordidxs for m in candidates]))
  nounidxs = set([i for i in range(len(s.words)) if s.poses[i].startswith("NN")])
  x = sorted(list(nounidxs - covered))
  if len(x) > 0:
    ridxs = [random.randint(0, len(x)-1)]
    while random.random() > 0.5:
      j = ridxs[-1]
      if j + 1 < len(x) and x[j+1] == x[j] + 1:
        ridxs.append(j+1)
      else:
        break
    wordidxs = [x[j] for j in ridxs]
    negs.append(
      create_mention(s, wordidxs, [s.words[i] for i in wordidxs], None, 'RAND_NEG', False))
  return negs


### RUN ###
# extract and supervise mention candidates
candidates = []
for line in sys.stdin:
  s = parse_line(line)
  cs = extract_candidates_from_sentence(s)
  cs += negative_supervision(s, cs)
  candidates += cs

# print to stdout
for c in candidates:
  print_tsv_output(c)
