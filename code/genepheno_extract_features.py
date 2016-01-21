#!/usr/bin/env python
from treedlib_util import PTSVParser, print_tsv
from basic_features import get_relation_features

xml_relation_parser = PTSVParser([
  ('relation_id', 'text'),
  ('doc_id', 'text'),
  ('section_id', 'text'),
  ('sent_id', 'int'),
  ('gene_mention_id', 'text'),
  ('gene_wordidxs', 'int[]'),
  ('pheno_mention_id', 'text'),
  ('pheno_wordidxs', 'int[]'),
  ('xml', 'text')
])

for row in xml_relation_parser.parse_stdin():
  for feat in get_relation_features(row.xml, row.gene_wordidxs, row.pheno_wordidxs):
    print_tsv((row.doc_id, row.section_id, row.relation_id, feat))
