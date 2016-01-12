#! /usr/bin/env python

import collections
import extractor_util as util
import data_util as dutil
import dep_util as deps
import os
import random
import re
import sys
import config

import genepheno_supervision_util as sv

if __name__ == '__main__':
  sr = config.GENE_PHENO_CAUSATION['SR']
  print >> sys.stderr, sr
  hf = config.GENE_PHENO_CAUSATION['HF']
  sv.supervise(sr, hf)
