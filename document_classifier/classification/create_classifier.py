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

def load_labeled_docs_processed(data_path, neg_factor=None):
  b = Bunch()
  b.data = []
  b.pmids = []
  b.target = []
  poss = 0
  negs = 0
  include_pmids = set()
  with open(data_path) as f:
    ctr = -1
    for line in f:
      ctr += 1
      if ctr % 100000 == 0:
        print >>sys.stderr, "counting %d lines" % ctr
      item = line.strip().split('\t')
      pmid = item[0]
      data = item[1]
      label = int(item[2])
      if label == 1 or neg_factor is None or negs <= poss * neg_factor or pmid in include_pmids:
        include_pmids.add(pmid)
        b.pmids.append(pmid)
        b.data.append(data)
        b.target.append(label)
        if label == 1:
          poss += 1
        else:
          negs += 1
  return b

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print >>sys.stderr, "need 1 arg: path to training (pubmed) TSV"
    sys.exit(1)
  training_path = sys.argv[1]

  train_docs = load_labeled_docs_processed(training_path, 1.2)
  pos_count = np.count_nonzero(train_docs.target)
  print >>sys.stderr, "Number of positive training examples: %d" % pos_count
  neg_count = len(train_docs.target) - pos_count
  print >>sys.stderr, "Number of negative training examples: %d" % neg_count
  count_vect = CountVectorizer(analyzer='word', ngram_range=(1,1))
  print >>sys.stderr, "Count-vectorizing data"
  X_train_counts = count_vect.fit_transform(train_docs.data)
  tfidf_transformer = TfidfTransformer()
  print >>sys.stderr, "Transforming word counts to tf-idf"
  X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
  print >>sys.stderr, "Fitting classifier to data"
  clf = LogisticRegression(penalty='l2', max_iter=1000)
  clf.fit(X_train_tfidf, train_docs.target)
  with open('clf.pkl', 'wb') as f:
    cPickle.dump(clf, f)
  with open('count_vect.pkl', 'wb') as f:
    cPickle.dump(count_vect, f)
  with open('tfidf_transformer.pkl', 'wb') as f:
    cPickle.dump(tfidf_transformer, f)
