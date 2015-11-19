#! /usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import re

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print >>sys.stderr, "need 2 args: symbol for file (NOT used for stdin), output path"
    sys.exit(1)
  pubmed = sys.argv[1]
  out_path = sys.argv[2]
  gene_rgx = comp_gene_rgxs(ensembl_genes_path)
  with open(out_path, 'w') as f:
    ctr = -1
    for line in sys.stdin:
      ctr += 1
      if ctr % 500 == 0:
        print >>sys.stderr, "replacing %d lines in %s " % (ctr, pubmed)
      item = json.loads(line)
      pmid = item['doc-id']
      content = item['content']
      print "%s\t%s" % (pmid, content)
