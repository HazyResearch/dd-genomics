#!/usr/bin/env python
import sys
from treedlib_util import corenlp_parser, print_tsv_output
from treedlib_structs import corenlp_to_xmltree

for row in corenlp_parser.parse_stdin():
  xt = corenlp_to_xmltree(row)
  if xt is not None:
    print_tsv_output((row.doc_id, row.section_id, row.sent_id, xt.to_str()))
