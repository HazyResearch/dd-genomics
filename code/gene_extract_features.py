#!/usr/bin/env python
from collections import namedtuple
import extractor_util as util
import os
import sys
import ddlib

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'int'),
          ('words', 'text[]'),
          ('lemmas', 'text[]'),
          ('poses', 'text[]'),
          ('ners', 'text[]'),
          ('dep_paths', 'text[]'),
          ('dep_parents', 'int[]'),
          ('mention_id', 'text'),
          ('mention_type', 'text'),
          ('mention_wordidxs', 'int[]')])

Feature = namedtuple('Feature', ['doc_id', 'mention_id', 'name'])

ENSEMBL_TYPES = ['NONCANONICAL', 'CANONICAL', 'REFSEQ']


def get_features_for_row(row):
  features = []
  f = Feature(doc_id=row.doc_id, mention_id=row.mention_id, name=None)

  # (1) Get generic ddlib features
  sentence = util.create_ddlib_sentence(row)
  span = ddlib.Span(begin_word_id=row.mention_wordidxs[0], length=len(row.mention_wordidxs))
  features += [f._replace(name=feat) \
            for feat in ddlib.get_generic_features_mention(sentence, span) if not (feat.startswith("LEMMA_SEQ") or feat.startswith("WORD_SEQ"))]
  
  # (2) Include gene type as a feature
  for t in ENSEMBL_TYPES:
    if re.search(re.escape(t), row.mention_type, flags=re.I):
      features.append(f._replace(name='GENE_TYPE[%s]' % t))
      break
  return features

if __name__ == '__main__':
  util.run_main_tsv(row_parser=parser.parse_tsv_row, row_fn=get_features_for_row)
