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
def lemmatize(w):
  if w.isalpha():
    return lemmatizer.lemmatize(w)
  else:
    # Things involving non-alphabetic characters, don't try to lemmatize
    return w

STOPWORDS = [w.strip() for w in open('%s/onto/manual/stopwords.tsv' % (GDD_HOME,), 'rb')]

def normalize_phrase(p):
  """Lowercases, removes stop words, and lemmatizes inputted multi-word phrase"""
  out = []

  # split into contiguous alphanumeric segments, lower-case, filter stopwords, lemmatize
  ws = [re.sub(r'[^a-z0-9]', '', w) for w in p.lower().split()]
  ws = [w for w in ws if w not in STOPWORDS]
  ws = [lemmatize(w) for w in ws]
  out.append(' '.join(ws))

  # if there's a comma, try permuting the order (some of these cases ommitted from HPO!)
  if ',' in p:
    cs = re.split(r'\s*,\s*', p.strip())
    out += normalize_phrase(' '.join(cs[::-1]))
  return out

def load_diseases(filename):
  out = []
  for line in open(filename):
    row = line.split('\t')
    omim_ps_id = row[0]
    names = row[1].split('|^|')
    alt_names = row[2].split('|^|')
    forms = []
    exact = []
    for p in names:
      if len(p.strip().lower()) > 0 and len(p.strip().split()) > 1:
        exact.append(p.strip().lower())
        forms.append((omim_ps_id, p.strip().lower(), 'EXACT'))
    for p in alt_names:
      if len(p.strip().lower()) > 0 and len(p.strip().split()) > 1:
        exact.append(p.strip().lower())
        forms.append((omim_ps_id, p.strip().lower(), 'EXACT'))
    for p in exact:
      forms += [(omim_ps_id, np.strip(), 'LEMMA') for np in normalize_phrase(p) if len(np.strip()) > 0 and len(np.strip().split()) > 1]
    for f in forms:
      k = f[0] + f[1]
      if not seen.has_key(k):
        seen[k] = 1
        out.append(f)
  return out

if __name__ == "__main__":
  out_pheno = []
  out_disease = []
  seen = {}
  
  load_data_tsv = lambda f : [line.split('\t') for line in open('%s/onto/data/%s' % (GDD_HOME, f), 'rb')]
  for row in load_data_tsv('hpo_phenotypes.tsv'):
    hpo_id = row[0]
    exact = [row[1].lower()]
    if len(row) > 2:
      exact += [p.strip().lower() for p in row[2].split('|') if len(p.strip()) > 0]
    forms = [(hpo_id, p, "EXACT") for p in exact]
    for p in exact:
      forms += [(hpo_id, np, "LEMMA") for np in normalize_phrase(p) if len(np.strip()) > 0]
    for f in forms:
      k = f[0] + f[1]
      if not seen.has_key(k):
        seen[k] = 1
        out_pheno.append(f)

  out_disease.extend(load_diseases('%s/onto/manual/phenotypic_series.tsv' % GDD_HOME))
  out_disease.extend(load_diseases('%s/onto/manual/diseases.tsv' % GDD_HOME))

  with open("%s/onto/manual/pheno_terms.tsv" % (GDD_HOME,), 'w') as f:
    for o in out_pheno:
      f.write('\t'.join(o))
      f.write('\n')
  with open("%s/onto/manual/disease_terms.tsv" % (GDD_HOME,), 'w') as f:
    for o in out_disease:
      f.write('\t'.join(o))
      f.write('\n')
