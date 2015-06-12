#!/usr/bin/env python
from collections import defaultdict, namedtuple
import sys
import re
import os
import random
from itertools import chain
import extractor_util as util
from data_util import get_hpo_phenos, get_pubmed_id_for_doc, read_doi_to_pmid, read_hpo_dag

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]')])

# This defines the output Mention object
Mention = namedtuple('Mention', [
            'dd_id',
            'doc_id',
            'sent_id',
            'wordidxs',
            'mention_id',
            'mention_type',
            'entity',
            'words',
            'is_correct'])

# Load stop words list
# [See onto/gen_basic_stopwords.py]
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)
STOPWORDS = frozenset([w.strip() for w in open(onto_path('manual/stopwords.tsv'), 'rb')])

# Load list of english words
ENGLISH_WORDS = frozenset([w.strip() for w in open(onto_path('data/english_words.tsv'), 'rb')])

# Load the HPO DAG
hpo_dag = read_hpo_dag()
hpo_phenos = set(get_hpo_phenos(hpo_dag))

# Load map from DOI to PMID, for PLoS documents
DOI_TO_PMID = read_doi_to_pmid()

# Load map from Pubmed ID to HPO term (via MeSH)
PMID_TO_HPO = defaultdict(set)
for line in open(onto_path('data/hpo_to_pmid_via_mesh.tsv')):
  hpo_id, pmid = line.strip().split('\t')
  PMID_TO_HPO[pmid].add(hpo_id)


# Load phenotypes (as phrases + as frozensets to allow permutations)
# [See onto/prep_pheno_terms.py]
# NOTE: for now, we don't distinguish between lemmatized / exact
PHENOS = {}
PHENO_SETS = {}
rows = [line.split('\t') for line in open(onto_path('data/pheno_terms.tsv'), 'rb')]
for row in rows:
  hpoid, phrase, entry_type = [x.strip() for x in row]
  if hpoid in hpo_phenos:
    if phrase in PHENOS:
      PHENOS[phrase].append(hpoid)
    else:
      PHENOS[phrase] = [hpoid]
    phrase_bow = frozenset(phrase.split())
    if phrase_bow in PHENO_SETS:
      PHENO_SETS[phrase_bow].append(hpoid)
    else:
      PHENO_SETS[phrase_bow] = [hpoid]


### CANDIDATE EXTRACTION + POSITIVE SUPERVISION ###
MAX_LEN = 8
def extract_candidates(tokens, s):
  """Extracts candidate phenotype mentions from a (filtered) list of token tuples"""
  if len(tokens) == 0: return []
  candidates = []
  m = Mention(dd_id=None, doc_id=s.doc_id, sent_id=s.sent_id, wordidxs=None, mention_id=None, mention_type=None, entity=None, words=None, is_correct=None)

  # get all n-grams (w/ n <= MAX_LEN) and check for exact or exact lemma match
  # we go through n in descending order to prefer the longest possible exact match
  for l in reversed(range(1, min(len(tokens), MAX_LEN+1))):
    for start in range(len(tokens)-l+1):
      wordidxs, words, lemmas = zip(*tokens[start:(start+l)])

      # (1) Check for exact match (including exact match of lemmatized / stop words removed)
      phrase, lemma_phrase = [' '.join(x) for x in (words, lemmas)]
      if phrase in PHENOS or lemma_phrase in PHENOS:
        entities = PHENOS[phrase] if phrase in PHENOS else PHENOS[lemma_phrase]

        # handle exact / exact lemma matches recursively to exclude overlapping mentions
        mtype = 'EXACT'
        for entity in entities:
          mid = '%s_%s_%s_%s_%s_%s' % (s.doc_id,s.sent_id,wordidxs[0],wordidxs[-1],mtype,entity)
          candidates.append(
            m._replace(wordidxs=wordidxs, words=words, entity=entity, mention_id=mid, mention_type=mtype))
        return candidates + extract_candidates(tokens[:start], s) \
                          + extract_candidates(tokens[start+l:], s)

      # (2) Check for permuted match
      phrase_set, lemma_set = [frozenset(x) for x in (words, lemmas)]
      if phrase_set in PHENO_SETS or lemma_set in PHENO_SETS:
        entities = PHENO_SETS[phrase_set] if phrase_set in PHENO_SETS else PHENO_SETS[lemma_set]
        mtype = 'PERM'
        for entity in entities:
          mid = '%s_%s_%s_%s_%s_%s' % (s.doc_id,s.sent_id,wordidxs[0],wordidxs[-1],mtype,entity)
          candidates.append(
            m._replace(wordidxs=wordidxs, words=words, entity=entity, mention_id=mid,
              mention_type=mtype))

      # (3) Check for an exact match with one ommitted (interior) word/lemma
      if len(words) > 2:
        for j in range(1,len(words)-1):
          phrase, lemma_phrase = [' '.join([w for i,w in enumerate(x) if i != j]) \
                                    for x in (words, lemmas)]
          if phrase in PHENOS or lemma_phrase in PHENOS:
            entities = PHENOS[phrase] if phrase in PHENOS else PHENOS[lemma_phrase]
            mtype = 'OMIT_%s' % j
            for entity in entities:
              mid='%s_%s_%s_%s_%s_%s'%(s.doc_id,s.sent_id,wordidxs[0],wordidxs[-1],mtype,entity)
              candidates.append(
                m._replace(wordidxs=wordidxs, words=words, entity=entity, mention_id=mid,
                  mention_type=mtype))
  return candidates


def extract_candidates_from_sentence(s):
  """Extracts candidate phenotype mentions from an input line as Sentence object"""

  # Skip row if sentence doesn't contain a verb, contains URL, etc.
  if util.skip_row(s):
    return []

  # Split into list of token tuples & process recursively
  tokens = [(i, s.words[i].lower(), s.lemmas[i]) for i in range(len(s.words))]
  tokens = filter(lambda t : t[1] not in STOPWORDS and len(t[1]) > 2, tokens)
  return extract_candidates(tokens, s)


COMMON_WORD_PROB = 0.1
def get_mention_supervision(row, mention):
  """Get the supervision for a candidate mention"""

  # Filter as negative some based on specific rules- taking priority
  POST_NEG_MATCHES = r'cell(s|\slines?)?'
  phrase_post = " ".join(row.words[mention.wordidxs[-1]:])
  if re.search(POST_NEG_MATCHES, phrase_post, flags=re.I):
    return False

  # Supervise exact matches as true; however if exact match is also a common english word,
  # label true w.p. < 1
  if mention.mention_type == 'EXACT':
    if len(words) == 1 and phrase in ENGLISH_WORDS and random.random() < COMMON_WORD_PROB:
      return True
    else:
      return True

  # Add supervision via mesh terms
  pubmed_id = get_pubmed_id_for_doc(row.doc_id, doi_to_pmid=DOI_TO_PMID)
  if pubmed_id and pubmed_id in PMID_TO_HPO:
    known_hpo = PMID_TO_HPO[pubmed_id]
    if mention.entity in known_hpo:
      return True

    # If this is more specific than MeSH term, also consider true.
    elif mention.entity in hpo_dag.node_set:
      for parent in known_hpo:
        if hpo_dag.has_child(parent, mention.entity):
          return True
  return None


### NEGATIVE SUPERVISION ###
def generate_rand_negatives(s, candidates):
  """Generate some negative examples in 1:1 ratio with positive examples"""
  negs = []
  n_negs = len([c for c in candidates if c.is_correct])
  if n_negs == 0:
    return negs

  # pick random noun / adj phrases which do not overlap with candidate mentions
  covered = set(chain.from_iterable([m.wordidxs for m in candidates]))
  idxs = set([i for i in range(len(s.words)) if re.match(r'NN*|JJ*', s.poses[i])])

  for i in range(n_negs):
    x = sorted(list(idxs - covered))
    if len(x) == 0:
      break
    ridxs = [random.randint(0, len(x)-1)]
    while random.random() > 0.5:
      j = ridxs[-1]
      if j + 1 < len(x) and x[j+1] == x[j] + 1:
        ridxs.append(j+1)
      else:
        break
    wordidxs = [x[j] for j in ridxs]
    mtype = 'RAND_NEG'
    mid = '%s_%s_%s_%s_%s' % (s.doc_id, s.sent_id, wordidxs[0], wordidxs[-1], mtype)
    negs.append(
      Mention(dd_id=None, doc_id=s.doc_id, sent_id=s.sent_id, wordidxs=wordidxs,
        mention_id=mid, mention_type=mtype, entity=None, words=[s.words[i] for i in wordidxs],
        is_correct=False))
    for i in wordidxs:
      covered.add(i)
  return negs

def get_all_candidates_from_row(row):
  supervised_mentions = []
  for mention in extract_candidates_from_sentence(row):
    is_correct = get_mention_supervision(row, mention)
    supervised_mentions.append(mention._replace(is_correct=is_correct)
  supervised_mentions += generate_rand_negatives(row, supervised_mentions)
  return supervised_mentions


if __name__ == '__main__':
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_all_candidates_from_row)
