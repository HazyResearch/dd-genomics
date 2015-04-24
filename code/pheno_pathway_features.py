#!/usr/bin/env python
import sys

import extractor_util as util

def create_features(pheno, pathway_id):
  return ['same-pathway']

if __name__ == '__main__':
  for line in sys.stdin:
    pheno, pathway_id = line.strip().split('\t')
    features = create_features(pheno, pathway_id)
    for f in features:
      util.print_tsv_output((pheno, pathway_id, f))
