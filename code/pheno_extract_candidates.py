#!/usr/bin/env python
from collections import defaultdict, namedtuple
import sys
import re
import os
import random
from itertools import chain
import extractor_util as util
import data_util as dutil


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


def load_pmid_to_hpo():
  """Load map from Pubmed ID to HPO term (via MeSH)"""
  pmid_to_hpo = defaultdict(set)
  for line in open(onto_path('data/hpo_to_pmid_via_mesh.tsv')):
    hpo_id, pmid = line.strip().split('\t')
    pmid_to_hpo[pmid].add(hpo_id)
  return pmid_to_hpo


def load_pheno_terms():
  phenos = {}
  pheno_sets = {}
  """
  Load phenotypes (as phrases + as frozensets to allow permutations)
  Output a dict with pheno phrases as keys, and a dict with pheno sets as keys
  """

  # [See onto/prep_pheno_terms.py]
  # Note: for now, we don't distinguish between lemmatized / exact
  rows = [line.split('\t') for line in open(onto_path('data/pheno_terms.tsv'), 'rb')]
  for row in rows:
    hpoid, phrase, entry_type = [x.strip() for x in row]
    if hpoid in hpo_phenos:
      if phrase in phenos:
        phenos[phrase].append(hpoid)
      else:
        phenos[phrase] = [hpoid]
      phrase_bow = frozenset(phrase.split())
      if phrase_bow in pheno_sets:
        pheno_sets[phrase_bow].append(hpoid)
      else:
        pheno_sets[phrase_bow] = [hpoid]
  return phenos, pheno_sets


### CANDIDATE EXTRACTION ###

# HACK[Alex]: this maximum phenotype mention length is arbitrary... should be tested!
MAX_LEN = 8

def keep_word(w):
  return (w not in STOPWORDS and len(w) > 2)

def extract_candidate_mentions(row):
  """Extracts candidate phenotype mentions from an input row object"""
  mentions = []

  # First we initialize a list of indices which we 'split' on,
  # i.e. if a window intersects with any of these indices we skip past it
  split_indices = set()

  # split on certain characters / words e.g. commas
  SPLIT_LIST = frozenset([',', ';'])
  split_indices.update([i for i,w in enumerate(row.words) if w in SPLIT_LIST])

  # split on segments of more than 2 consecutive skip words
  seq = []
  for i,w in enumerate(row.words):
    if not keep_word(w):
      seq.append(i)
    else:
      if len(seq) > 2:
        split_indices.update(seq)
      seq = []

  # Next, pass a window of size n (dec.) over the sentence looking for candidate mentions
  m = Mention(dd_id=None, doc_id=row.doc_id, sent_id=row.sent_id, wordidxs=None, \
              words=None, mention_id=None, mention_type=None, entity=None, is_correct=None)
  for n in reversed(range(1, min(len(row.words), MAX_LEN)+1)):
    for i in range(len(row.words)-n+1):
      wordidxs = range(i,i+n)
      words = row.words[i:i+n]
      lemmas = row.lemmas[i:i+n]

      # skip this window if it intersects with the split set
      if not split_indices.isdisjoint(wordidxs):
        continue

      # skip this window if it is sub-optimal: e.g. starts with a skip word, etc.
      if not keep_word(words[0]) or not keep_word(words[-1]):
        continue
      
      mid_base = '%s_%s_%s_%s' % (row.doc_id, row.sent_id, i, i+n-1)
      ws = filter(keep_word, words)
      lws = filter(keep_word, lemmas)

      # (1) Check for exact match (including exact match of lemmatized / stop words removed)
      # If found add to split list so as not to consider subset phrases
      p, lp = map(' '.join, [ws, lws])
      if p in PHENOS or lp in PHENOS:
        entities = PHENOS[p] if p in PHENOS else PHENOS[lp]
        mention_type = 'EXACT'
        for entity in entities:
          mid = '%s_%s_%s' % (mid_base, mention_type, entity)
          mentions.append(m._replace(wordidxs=wordidxs, words=words, entity=entity, \
                                     mention_id=mid, mention_type=mention_type))
        split_indices.update(wordidxs)
        continue

      # (2) Check for permuted match
      # Note: avoid repeated words here!
      ps, lps = map(frozenset, [ws, lws])
      if (len(ps)==len(ws) and ps in PHENO_SETS) or (len(lps)==len(lws) and lps in PHENO_SETS):
        entities = PHENO_SETS[ps] if ps in PHENO_SETS else PHENO_SETS[lps]
        mention_type = 'PERM'
        for entity in entities:
          mid = '%s_%s_%s' % (mid_base, mention_type, entity)
          mentions.append(m._replace(wordidxs=wordidxs, words=words, entity=entity, \
                                     mention_id=mid, mention_type=mention_type))
        continue

      # (3) Check for an exact match with one ommitted (interior) word/lemma
      # Note: only consider ommiting non-stop words!
      if len(ws) > 2:
        for omit in range(1, len(ws)-1):
          p, lp = [' '.join([w for i,w in enumerate(x) if i != omit]) for x in [ws, lws]]
          if p in PHENOS or lp in PHENOS:
            entities = PHENOS[p] if p in PHENOS else PHENOS[lp]
            mention_type = 'OMIT_%s' % omit
            for entity in entities:
              mid = '%s_%s_%s' % (mid_base, mention_type, entity)
              mentions.append(m._replace(wordidxs=wordidxs, words=words, entity=entity, \
                                         mention_id=mid, mention_type=mention_type))
  return mentions    


### DISTANT SUPERVISION ###
COMMON_WORD_PROB = 0.1
def get_mention_supervision(row, mention):
  """Get the supervision for a candidate mention"""

  # Filter as negative some based on specific rules- taking priority
  POST_NEG_MATCHES = r'cell(s|\slines?)?'
  phrase_post = " ".join(row.words[mention.wordidxs[-1]:])
  if re.search(POST_NEG_MATCHES, phrase_post, flags=re.I):
    return False, 'CELL_LINES'

  # Add supervision via mesh terms
  pubmed_id = dutil.get_pubmed_id_for_doc(row.doc_id, doi_to_pmid=DOI_TO_PMID)
  if pubmed_id and pubmed_id in PMID_TO_HPO:
    known_hpo = PMID_TO_HPO[pubmed_id]
    if mention.entity in known_hpo:
      return True, mention.mention_type + '_MESH_SUPERV'

    # If this is more specific than MeSH term, also consider true.
    elif mention.entity in hpo_dag.node_set:
      for parent in known_hpo:
        if hpo_dag.has_child(parent, mention.entity):
          return True, mention.mention_type + '_MESH_CHILD_SUPERV'

  # Supervise exact matches as true; however if exact match is also a common english word,
  # label true w.p. < 1
  phrase = " ".join(mention.words).lower()
  if mention.mention_type == 'EXACT':
    if len(row.words) == 1 and phrase in ENGLISH_WORDS and random.random() < COMMON_WORD_PROB:
      return True, 'EXACT_AND_ENGLISH_WORD'
    else:
      return True, 'EXACT'

  # Else default to existing values / NULL
  return None, mention.mention_type


### RANDOM NEGATIVE SUPERVISION ###
def generate_rand_negatives(s, candidates):
  """Generate some negative examples in 1:1 ratio with positive examples"""
  negs = []
  n_negs = len([c for c in candidates if c.is_correct])
  if n_negs == 0:
    return negs

  # pick random noun / adj phrases which do not overlap with candidate mentions
  covered = set(chain.from_iterable([m.wordidxs for m in candidates]))
  idxs = set([i for i in range(len(s.words)) if re.match(r'NN.?|JJ.?', s.poses[i])])

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
  for mention in extract_candidate_mentions(row):
    is_correct, mention_type = get_mention_supervision(row, mention)
    supervised_mentions.append(mention._replace(is_correct=is_correct,mention_type=mention_type))
  supervised_mentions += generate_rand_negatives(row, supervised_mentions)
  return supervised_mentions


if __name__ == '__main__':
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

  # Load static dictionaries
  # TODO: any simple ways to speed this up? 
  STOPWORDS = frozenset([w.strip() for w in open(onto_path('manual/stopwords.tsv'), 'rb')])
  ENGLISH_WORDS = frozenset([w.strip() for w in open(onto_path('data/english_words.tsv'), 'rb')])
  hpo_dag = dutil.read_hpo_dag()
  hpo_phenos = set(dutil.get_hpo_phenos(hpo_dag))
  DOI_TO_PMID = dutil.read_doi_to_pmid()
  PMID_TO_HPO = load_pmid_to_hpo()
  PHENOS, PHENO_SETS = load_pheno_terms()

  # Read TSV data in as Row objects
  for line in sys.stdin:
    print line
    row = parser.parse_tsv_row(line)

    # Skip row if sentence doesn't contain a verb, contains URL, etc.
    if util.skip_row(row):
      continue

    # find candidate mentions & supervise
    try:
      mentions = get_all_candidates_from_row(row)
    except IndexError:
      util.print_error("Error with row: %s" % (row,))
      continue

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
