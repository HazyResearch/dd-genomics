#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import re

def load_unlabeled_docs(data_path):
  rv = {}
  print >>sys.stderr, "Loading JSON data"
  ctr = -1
  with open(data_path) as f:
    for line in f:
      ctr += 1
      if ctr % 100000 == 0:
        print >>sys.stderr, "counting %d lines" % ctr
      item = json.loads(line)
      pmid = item['doc-id']
      content = item['content']
      content.replace('\n', ' ')
      print "%s\t%s" % (pmid, content.encode('ascii', 'ignore'))

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print >>sys.stderr, "need 1 arg: path to json"
    sys.exit(1)
  path = sys.argv[1]
  load_unlabeled_docs(path)
