#! /usr/bin/env python

import sys
import re

for line in sys.stdin:
  print re.sub(r'\W+', ' ', line.strip())
