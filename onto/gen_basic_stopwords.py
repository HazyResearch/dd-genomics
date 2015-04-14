#!/usr/bin/env python
import sys
import re
import os
from nltk.corpus import stopwords

# [Alex 4/12/15]:
# This just loads the default stopwords list from nltk and outputs this to onto/manual/stopwords.tsv
# Could also extend this to pull in other stopwords lists and combine
# The stopwords list is put into the manual folder because the intention is to have it be curated
# (could extend this script to be strictly additive re: the above...)
out = []
out += stopwords.words('english')

GDD_HOME = os.environ['GDD_HOME']
with open('%s/onto/manual/stopwords.tsv' % (GDD_HOME,), 'wb') as f:
  for o in out:
    f.write(o)
    f.write('\n')
