#!/usr/bin/env python
import sys
from treedlib_util import sentence_input_to_xml_input
from extractor_util import print_tsv_output

for line in sys.stdin:
  try:
    x = sentence_input_to_xml_input(line)
  except:
    pass
  if x is not None:
    print_tsv_output(x)
