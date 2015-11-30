#! /usr/bin/python
# -*- coding: utf-8 -*-

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import sys
from bunch import *
import numpy as np
import random
from sklearn.linear_model import LogisticRegression
from nltk.stem import WordNetLemmatizer
import re
import cPickle

def load_unlabeled_docs_processed(data_path):
  b = Bunch()
  b.data = []
  b.pmids = []
  with open(data_path) as f:
    ctr = -1
    for line in f:
      ctr += 1
      if ctr % 100000 == 0:
        print >>sys.stderr, "counting %d lines" % ctr
      item = line.strip().split('\t')
      pmid = item[0]
      data = item[1]
      b.pmids.append(pmid)
      b.data.append(data)
  return b

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print >>sys.stderr, "need 2 args: path to all (pubmed) TSV, output path"
    sys.exit(1)
  all_path = sys.argv[1]

  with open('clf.pkl', 'rb') as f:
    print >>sys.stderr, "Loading classifier for %s" % all_path
    clf = cPickle.load(f)
  with open('count_vect.pkl', 'rb') as f:
    print >>sys.stderr, "Loading count vectorizer for %s" % all_path
    count_vect = cPickle.load(f)
  with open('tfidf_transformer.pkl', 'rb') as f:
    print >>sys.stderr, "Loading tfidf transformer for %s" % all_path
    tfidf_transformer = cPickle.load(f)

  print >>sys.stderr, "Loading all docs"
  docs_new = load_unlabeled_docs_processed(all_path)
  print >>sys.stderr, "Number of docs: %d" % len(docs_new.data)
  print >>sys.stderr, "Transforming new docs through count vectorization"
  X_new_counts = count_vect.transform(docs_new.data)
  print >>sys.stderr, "Transforming new docs through tf-idf"
  X_new_tfidf = tfidf_transformer.transform(X_new_counts)
  print >>sys.stderr, "Predicting over new docs"
  predicted = clf.predict(X_new_tfidf)
  print >>sys.stderr, "Printing to %s" % sys.argv[2]
  with open(sys.argv[2], 'w') as f:
    for i, value in enumerate(predicted):
      if value == 1:
        print >>f, docs_new.pmids[i]
