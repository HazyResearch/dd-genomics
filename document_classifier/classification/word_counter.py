#! /usr/bin/python
# -*- coding: utf-8 -*-

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import sys
from bunch import *
import numpy as np
import random
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import metrics
from nltk.stem import WordNetLemmatizer
import re
from nltk.corpus import stopwords
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostClassifier

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
  if len(sys.argv) != 4:
    print >>sys.stderr, "need 3 args: path to training (pubmed) TSV, path to testing (pubmed) TSV, path to random (pubmed) TSV"
    sys.exit(1)
  training_path = sys.argv[1]
  testing_path = sys.argv[2]
  random_path = sys.argv[3]

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
  # print >>sys.stderr, "Converting to dense matrix"
  # X_train_tfidf_dense = X_train_tfidf.toarray()
  print >>sys.stderr, "Fitting classifier to data"
  # clf = MultinomialNB(alpha=1.0).fit(X_train_tfidf, train_docs.target) # poor performance
  # clf = LogisticRegression().fit(X_train_tfidf, train_docs.target) # better performance but hoping for more
  # SVMs with kernel too slow
  # linear SVM like LogReg, but faster
  # clf = Pipeline([('feature-selection', SelectFromModel(LinearSVC(penalty='l1', dual=False))),
  #                 ('classification', GradientBoostingClassifier(n_estimators=100))]) # slow as number of estimators rises; but also 3% precision
  # clf = Pipeline([('anova', SelectKBest(f_regression, k=5)), ('clf', GradientBoostingClassifier(n_estimators=100))]) # too slow
  # clf = Pipeline([('feature-selection', SelectFromModel(LinearSVC(penalty='l1', dual=False))),
  #                 ('classification', SVC())]) # SVC still too slow
  # clf = Pipeline([('reduce-dim', PCA(n_components=100)),
  #                 ('classification', SVC())]) # SVC (? or PCA??) still too slow
  # PCA itself is far too slow! --- and apparently it doesn't help: linearsvc + pca 100 + gradient boosting 100 = worse than w/o pca
  # clf = Pipeline([('feature-selection', SelectFromModel(LinearSVC(penalty='l1', dual=False))),
  #                 ('classification', GradientBoostingClassifier(n_estimators=100))]) # this gives the old 3% and quite slow
  # clf = AdaBoostClassifier(base_estimator=LogisticRegression(solver='sag', max_iter=1000), n_estimators=200) # fitting depends highly on n_estimators. at 100, 0.11 / 0.76 or so
  clf = LogisticRegression(penalty='l2', max_iter=1000)

  clf.fit(X_train_tfidf, train_docs.target)

  print >>sys.stderr, "Loading test set"
  test_docs = load_labeled_docs_processed(testing_path)
  pos_count = np.count_nonzero(test_docs.target)
  print >>sys.stderr, "Number of positive testing examples: %d" % pos_count
  neg_count = len(test_docs.target) - pos_count
  print >>sys.stderr, "Number of negative testing examples: %d" % neg_count
  print >>sys.stderr, "Count-vectorizing test set"
  X_test_counts = count_vect.transform(test_docs.data)
  print >>sys.stderr, "Transforming test test to tf-idf"
  X_test_tfidf = tfidf_transformer.transform(X_test_counts)
  # print >>sys.stderr, "Converting to dense matrix"
  # X_test_tfidf_dense = X_test_tfidf.toarray()
  print >>sys.stderr, "Predicting over test set"
  predicted = clf.predict(X_test_tfidf)
  print >>sys.stderr, metrics.classification_report(test_docs.target, predicted, target_names=['uninteresting', 'OMIM'])

  print >>sys.stderr, "Loading random docs"
  docs_new = load_unlabeled_docs_processed(random_path)
  print >>sys.stderr, "Number of new docs: %d" % len(docs_new.data)
  print >>sys.stderr, "Transforming new docs through count vectorization"
  X_new_counts = count_vect.transform(docs_new.data)
  print >>sys.stderr, "Transforming new docs through tf-idf"
  X_new_tfidf = tfidf_transformer.transform(X_new_counts)
  # print >>sys.stderr, "Converting to dense matrix"
  # X_new_tfidf_dense = X_new_tfidf.toarray()
  print >>sys.stderr, "Predicting over new docs"
  predicted = clf.predict(X_new_tfidf)
  for i, value in enumerate(predicted):
    if value == 1:
      print("%s\t%s" % (docs_new.pmids[i], docs_new.data[i].decode('utf-8').encode('ascii', 'ignore')))
