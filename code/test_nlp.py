#! /usr/bin/env python

import dep_util
import extractor_util as util
import sys

# This defines the Row object that we read in to the extractor
parser = util.RowParser([
          ('doc_id', 'text'),
          ('sent_id', 'text'),
          ('dep_parents', 'int[]'),
          ('dep_paths', 'text[]'),
          ('words', 'text[]')])

if __name__ == "__main__":
  for line in sys.stdin:
    row = parser.parse_tsv_row(line)
    dpd = dep_util.DepPathDAG(row.dep_parents, row.dep_paths, row.words)
    for i in xrange(0, len(row.words)):
      sys.stderr.write(str((i, row.words[i], dpd.neighbors(i), [row.words[i] for i in dpd.neighbors(i)])) + '\n')
