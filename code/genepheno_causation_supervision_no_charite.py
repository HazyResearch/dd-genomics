#! /usr/bin/env python

import sys
import config

import genepheno_supervision_util as sv

if __name__ == '__main__':
  sr = config.GENE_PHENO_CAUSATION['SR']
  hf = config.GENE_PHENO_CAUSATION['HF']
  sv.supervise(sr, hf, charite_allowed=False)
