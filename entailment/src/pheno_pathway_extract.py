#!/usr/bin/env python
import sys

import extractor_util as util

if __name__ == '__main__':
  for line in sys.stdin:
    pheno, pathway_id = line.strip().split('\t')
    util.print_tsv_output((None, pheno, pathway_id, None))
