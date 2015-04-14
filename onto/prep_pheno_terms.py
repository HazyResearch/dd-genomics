#!/usr/bin/env python
import sys
import re
import os
#from nltk.stem.snowball import SnowballStemmer
#from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
GDD_HOME = os.environ['GDD_HOME']

# [Alex 4/12/15]:
# This script is for preprocessing a dictionary of phenotype phrase - HPO code pairs to be used
# primarily in the candidate extraction stage of the phenotype pipeline
# Currently we take the list of phenotype names and synonym phrases and normalize (lower case,
# lemmatization, stop words removal, etc).  Note that we also keep the exact form as well

# Choose which lemmatizer / stemmer to use
# Based on some rough testing:
# - WordNetLemmatizer has an error rate of ~10% wrt lemmatization of raw data in db (this is mostly verbs since we don't use POS tag info, and would be << 10% if only counting unique words)
# - SnowballStemmer is much faster but has ~30% error rate
# TODO: preprocess using Stanford CoreNLP lemmatizer for exact alignment w raw data?
lemmatizer = WordNetLemmatizer()
lemmatize = lambda w : lemmatizer.lemmatize(w)

# STOPWORDS list
STOPWORDS = [w.strip() for w in open('%s/onto/manual/stopwords.tsv' % (GDD_HOME,), 'rb')]

# TODO: permute word order if there is a comma, e.g. - "HP:0000221      tongue, fissured"
# TODO: --> why is the above one not getting handled...?
# TODO: remove non-alphabetic!
def normalize_phrase(p):
  """Lowercases, removes stop words, and lemmatizes inputted multi-word phrase"""
  out = []

  # split into contiguous alphabetic segments, lower-case, filter stopwords, lemmatize
  ws = [re.sub(r'[^a-z]', '', w) for w in p.lower().split()]
  ws = [w for w in ws if len(w) > 2 and w not in STOPWORDS]
  ws = [lemmatize(w) for w in ws]
  out.append(' '.join(ws))

  # if there's a comma, try permuting the order (some of these cases ommitted from HPO!)
  if ',' in p:
    cs = re.split(r'\s*,\s*', p.strip())
    out += normalize_phrase(' '.join(cs[::-1]))
  return out

# output a list of (hpo-id, phrase, type) tuples where type is one of:
# "EXACT" - exact entry (lowercased)
# "LEMMA" - lemmatized version
out = []
seen = {}

# Load the dictionaries
load_data_tsv = lambda f : [line.split('\t') for line in open('%s/onto/data/%s' % (GDD_HOME, f), 'rb')]

# HPO
for row in load_data_tsv('hpo_phenotypes.tsv'):
  hpo_id = row[0]
  exact = [row[1].lower()]

  # Use the |-delimited list of synonyms supplied by the HPO as well
  if len(row) > 2:
    exact += [p.strip().lower() for p in row[2].split('|') if len(p.strip()) > 0]
  forms = [(hpo_id, p, "EXACT") for p in exact]

  # normalize_phrase returns a list that way we can easily do e.g. word permutation operations here 
  for p in exact:
    forms += [(hpo_id, np, "LEMMA") for np in normalize_phrase(p) if len(np.strip()) > 0]
  
  # Add unique HPO_ID - phrase pairs to output list
  for f in forms:
    k = f[0] + f[1]
    if not seen.has_key(k):
      seen[k] = 1
      out.append(f)

# output
with open("%s/onto/data/pheno_terms.tsv" % (GDD_HOME,), 'wb') as f:
  for o in out:
    f.write('\t'.join(o))
    f.write('\n')
