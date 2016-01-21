#!/usr/bin/env python
import sys
from treedlib_util import PTSVParser, print_tsv
from treedlib_structs import corenlp_to_xmltree

# The default PTSVParser config for raw sentence input
corenlp_parser = PTSVParser([
  ('doc_id', 'text'),
  ('section_id', 'text'),
  ('sent_id', 'int'),
  ('words', 'text[]'),
  ('lemmas', 'text[]'),
  ('poses', 'text[]'),
  ('ners', 'text[]'),
  ('dep_paths', 'text[]'),
  ('dep_parents', 'int[]')])

for row in corenlp_parser.parse_stdin():
  xt = corenlp_to_xmltree(row)
  if xt is not None:
    print_tsv((row.doc_id, row.section_id, row.sent_id, xt.to_str()))
