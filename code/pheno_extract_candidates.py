#!/usr/bin/env python
from collections import defaultdict, namedtuple
import sys
import re
import os
import random
from itertools import chain
import extractor_util as util
import data_util as dutil
import config


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
            'mention_supertype',
            'mention_subtype',
            'entity',
            'words',
            'is_correct'])


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
HF = config.PHENO['HF']
SR = config.PHENO['SR']

def keep_word(w):
  return (w.lower() not in STOPWORDS and len(w) > HF['min-word-len'] - 1)

def extract_candidate_mentions(row):
  """Extracts candidate phenotype mentions from an input row object"""
  mentions = []

  # First we initialize a list of indices which we 'split' on,
  # i.e. if a window intersects with any of these indices we skip past it
  split_indices = set()

  # split on certain characters / words e.g. commas
  split_indices.update([i for i,w in enumerate(row.words) if w in HF['split-list']])

  # split on segments of more than M consecutive skip words
  seq = []
  for i,w in enumerate(row.words):
    if not keep_word(w):
      seq.append(i)
    else:
      if len(seq) > HF['split-max-stops']:
        split_indices.update(seq)
      seq = []

  # Next, pass a window of size n (dec.) over the sentence looking for candidate mentions
  for n in reversed(range(1, min(len(row.words), HF['max-len'])+1)):
    for i in range(len(row.words)-n+1):
      wordidxs = range(i,i+n)
      words = [w.lower() for w in row.words[i:i+n]]
      lemmas = [w.lower() for w in row.lemmas[i:i+n]]

      # skip this window if it intersects with the split set
      if not split_indices.isdisjoint(wordidxs):
        continue

      # skip this window if it is sub-optimal: e.g. starts with a skip word, etc.
      if not all(map(keep_word, [words[0], lemmas[0], words[-1], lemmas[-1]])):
        continue
      
      # Note: we filter stop words coordinated between word and lemma lists
      # (i.e. if lemmatized version of a word is stop word, it should be stop word too)
      # This also keeps these filtered lists in sync!
      ws, lws = zip(*[(words[k], lemmas[k]) for k in range(n) if keep_word(words[k]) and keep_word(lemmas[k])])

      # (1) Check for exact match (including exact match of lemmatized / stop words removed)
      # If found add to split list so as not to consider subset phrases
      p, lp = map(' '.join, [ws, lws])
      if p in PHENOS or lp in PHENOS:
        entities = PHENOS[p] if p in PHENOS else PHENOS[lp]
        for entity in entities:
          mentions.append(create_supervised_mention(row, wordidxs, entity, 'EXACT'))
        split_indices.update(wordidxs)
        continue

      # (2) Check for permuted match
      # Note: avoid repeated words here!
      if HF['permuted']:
        ps, lps = map(frozenset, [ws, lws])
        if (len(ps)==len(ws) and ps in PHENO_SETS) or (len(lps)==len(lws) and lps in PHENO_SETS):
          entities = PHENO_SETS[ps] if ps in PHENO_SETS else PHENO_SETS[lps]
          for entity in entities:
            mentions.append(create_supervised_mention(row, wordidxs, entity, 'PERM'))
          continue

      # (3) Check for an exact match with one ommitted (interior) word/lemma
      # Note: only consider ommiting non-stop words!
      if HF['omitted-interior']:
        if len(ws) > 2:
          for omit in range(1, len(ws)-1):
            p, lp = [' '.join([w for i,w in enumerate(x) if i != omit]) for x in [ws, lws]]
            if p in PHENOS or lp in PHENOS:
              entities = PHENOS[p] if p in PHENOS else PHENOS[lp]
              for entity in entities:
                mentions.append(create_supervised_mention(row, wordidxs, entity, 'OMIT_%s' % omit))
  return mentions    


### DISTANT SUPERVISION ###
VALS = config.PHENO['vals']
def create_supervised_mention(row, idxs, entity=None, mention_supertype=None, mention_subtype=None):
  """Given a Row object consisting of a sentence, create & supervise a Mention output object"""
  words = [row.words[i] for i in idxs]
  mid = '%s_%s_%s_%s_%s_%s' % (row.doc_id, row.sent_id, idxs[0], idxs[-1], mention_supertype, entity)
  m = Mention(None, row.doc_id, row.sent_id, idxs, mid, mention_supertype, mention_subtype, entity, words, None)

  if SR.get('post-match'):
    opts = SR['post-match']
    phrase_post = " ".join(row.words[idxs[-1]:])
    for name,val in VALS:
      if len(opts[name]) + len(opts['%s-rgx' % name]) > 0:
        match = util.rgx_mult_search(opts[name], opts['%s-rgx' % name], phrase_post, flags=re.I)
        if match:
          return m._replace(is_correct=val, mention_supertype='POST_MATCH_%s_%s' % (name, val), mention_subtype=match)

  if SR.get('mesh-supervise'):
    pubmed_id = dutil.get_pubmed_id_for_doc(row.doc_id, doi_to_pmid=DOI_TO_PMID)
    if pubmed_id and pubmed_id in PMID_TO_HPO:
      if entity in PMID_TO_HPO[pubmed_id]:
        return m._replace(is_correct=True, mention_supertype='%s_MESH_SUPERV' % mention_supertype, mention_subtype=str(pubmid_id) + ' ::: ' + str(entity))
  
      # If this is more specific than MeSH term, also consider true.
      elif SR.get('mesh-specific-true') and entity in hpo_dag.node_set:
        for parent in PMID_TO_HPO[pubmed_id]:
          if hpo_dag.has_child(parent, entity):
            return m._replace(is_correct=True, mention_supertype='%s_MESH_CHILD_SUPERV' % mention_supertype, mention_subtype=str(parent) + ' -> ' + str(entity))

  phrase = " ".join(words).lower()
  if mention_supertype == 'EXACT':
    if SR.get('exact-english-word') and \
      len(words) == 1 and phrase in ENGLISH_WORDS and random.random() < SR['exact-english-word']['p']:
      return m._replace(is_correct=True, mention_supertype='EXACT_AND_ENGLISH_WORD', mention_subtype=phrase)
    else:
      return m._replace(is_correct=True, mention_supertype='NON_EXACT_AND_ENGLISH_WORD', mention_subtype=phrase)

  # Else default to existing values / NULL
  return m


### RANDOM NEGATIVE SUPERVISION ###
def generate_rand_negatives(s, candidates):
  """Generate some negative examples in 1:1 ratio with positive examples"""
  negs = []
  n_negs = len([c for c in candidates if c.is_correct])
  if n_negs == 0:
    return negs

  # pick random noun / adj phrases which do not overlap with candidate mentions
  covered = set(chain.from_iterable([m.wordidxs for m in candidates]))
  idxs = set([i for i in range(len(s.words)) if re.match(SR['rand-negs']['pos-tag-rgx'], s.poses[i])])

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
        mention_id=mid, mention_supertype=mtype, mention_subtype=None, entity=None, words=[s.words[i] for i in wordidxs],
        is_correct=False))
    for i in wordidxs:
      covered.add(i)
  return negs


if __name__ == '__main__':
  onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

  # Load static dictionaries
  # TODO: any simple ways to speed this up? 
  STOPWORDS = frozenset([w.strip() for w in open(onto_path('manual/stopwords.tsv'), 'rb')])
  ENGLISH_WORDS = frozenset([w.strip() for w in open(onto_path('data/english_words.tsv'), 'rb')])
  hpo_dag = dutil.read_hpo_dag()
  hpo_phenos = set(dutil.get_hpo_phenos(hpo_dag))
  DOI_TO_PMID = dutil.read_doi_to_pmid()
  PMID_TO_HPO = dutil.load_pmid_to_hpo()
  PHENOS, PHENO_SETS = load_pheno_terms()

  # Read TSV data in as Row objects
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)

    # Skip row if sentence doesn't contain a verb, contains URL, etc.
    if util.skip_row(row):
      continue

    # find candidate mentions & supervise
    try:
      mentions = extract_candidate_mentions(row)
      if SR.get('rand-negs'):
        mentions += generate_rand_negatives(row, mentions)
    except IndexError:
      util.print_error("Error with row: %s" % (row,))
      continue

    # print output
    for mention in mentions:
      util.print_tsv_output(mention)
