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
  supervision_rules = config.GENE_PHENO['association']['SR']
  sv.supervise(supervision_rules)
