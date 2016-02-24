#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import ddlib
import config
import sys
import re

parser = util.RowParser([
          ('relation_id', 'text'),
          ('doc_id', 'text'),
          ('section_id', 'text'),
          ('sent_id', 'int'),
          ('gene_mention_id', 'text'),
          ('gene_wordidxs', 'int[]'),
          ('pheno_mention_id', 'text'),
          ('pheno_wordidxs', 'int[]'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]')])

fr = config.GENE_PHENO['F']

Feature = namedtuple('Feature', ['doc_id', 'section_id', 'relation_id', 'name'])

bad_features = ['STARTS_WITH_CAPITAL_\[True_True\]', 'NGRAM_1_\[to\]', 
                'NGRAM_1_\[a\]','NGRAM_1_\[and\]', 'NGRAM_1_\[in\]', 'IS_INVERTED',
                'NGRAM_1_\[or\]', 'NGRAM_1_\[be\]', 'NGRAM_1_\[with\]',
                'NER_SEQ_\[[O ]*\]$', 'W_NER_L_1_R_1_[\[\]O_]*$',
                'LENGTHS_[0_1]', 'W_NER_L_[0-9]_R_[0-9]_[\[\] O_]*$',
                'LENGTHS_\[[0-9]_[0-9]\]']
inv_bad_features = []
for f in bad_features:
  inv_bad_features.append('INV_' + f)
bad_features.extend(inv_bad_features)

def create_ners_between(gene_wordidxs, pheno_wordidxs, ners):
  if gene_wordidxs[0] < pheno_wordidxs[0]:
    start = max(gene_wordidxs) + 1
    end = min(pheno_wordidxs) - 1
  else:
    start = max(pheno_wordidxs) + 1
    end = min(gene_wordidxs) - 1
  prefix = 'NERS_BETWEEN_'
  nonnull_ners = []
  for i in xrange(start, end + 1):
    ner = ners[i]
    if ner != 'O':
      nonnull_ners.append('[' + ner + ']')
  rv = prefix + '_'.join(nonnull_ners)
  return [rv]

non_alnum = re.compile('[\W_]+')

def get_custom_features(row):
  phrase = ' '.join(row.words)
  lemma_phrase = ' '.join(row.lemmas)
  global_sentence_patterns = fr['global-sent-words']
  for p in global_sentence_patterns:
    if re.findall(p, phrase) or re.findall(p, lemma_phrase):
      yield 'GLOB_SENT_PATTERN_%s' % (non_alnum.sub('_', p))

def get_features_for_candidate(row):
  """Extract features for candidate mention- both generic ones from ddlib & custom features"""
  features = []
  f = Feature(doc_id=row.doc_id, section_id=row.section_id, relation_id=row.relation_id, name=None)
  dds = util.create_ddlib_sentence(row)

  # (1) GENERIC FEATURES from ddlib
  gene_span = ddlib.Span(begin_word_id=row.gene_wordidxs[0], length=len(row.gene_wordidxs))
  pheno_span = ddlib.Span(begin_word_id=row.pheno_wordidxs[0], length=len(row.pheno_wordidxs))
  for feat in ddlib.get_generic_features_relation(dds, gene_span, pheno_span):
    take = True
    for bad_feature_pattern in bad_features:
      # warning, match matches only from start of string
      if re.match(bad_feature_pattern, feat):
        take = False
        break
    if take:
      features.append(f._replace(name=feat))
  features.extend([f._replace(name=feat) for feat in get_custom_features(row)])
  # these seem to be hurting (?)
  # start_span = ddlib.Span(begin_word_id=0, length=4)
  # for feat in ddlib.get_generic_features_mention(dds, start_span, length_bin_size=2):
  #  features.append(f._replace(name='START_SENT_%s' % feat))
  # WITH these custom features, I get a little LESS precision and a little MORE recall (!)
  # features += [f._replace(name=feat) for feat in create_ners_between(row.gene_wordidxs, row.pheno_wordidxs, row.ners)]
  return features

# Helper for loading in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

if __name__ == '__main__':
  ddlib.load_dictionary_map(fr['synonyms'])
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_candidate)
