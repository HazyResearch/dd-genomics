#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib
from treedlib_util import read_ptsv, SentenceInput
from tree_structs import sentence_to_xmltree
from basic_features import get_relation_features


Feature = namedtuple('Feature', ['doc_id', 'section_id', 'relation_id', 'name'])

for line in sys.stdin:

  # Parse the TSV input line
  cols = read_ptsv(line)

  # Get the relation-level attributes
  relation_id = cols[0]
  doc_id = cols[1]
  section_id = cols[2]
  sent_id = cols[3]
  gene_mention_id = cols[4]
  gene_wordidxs = cols[5]
  pheno_mention_id = cols[6]
  pheno_wordidxs = cols[7]

  # Get the sentence and parse as XML
  # NOTE: This should be done as pre-processing!!
  si = SentenceInput._make(cols[8:] + [range(len(cols[8]))])
  t = sentence_to_xmltree(si)

  # Get relation features
  f = Feature(doc_id=doc_id, section_id=section_id, relation_id=relation_id, name=None)
  for feat in get_relation_features(t.root, gene_wordidxs, pheno_wordidxs):
    util.print_tsv_output(f._replace(name=feat))
