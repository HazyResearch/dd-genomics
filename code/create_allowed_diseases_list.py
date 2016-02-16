#! /usr/bin/env python

import config
import sys

if __name__ == "__main__":
  disallowed_phrases = config.PHENO['HF']['disallowed-phrases']
  for line in sys.stdin:
    take = True
    for dp in disallowed_phrases:
      if dp in line.lower():
        take = False
        break
    if take:
      sys.stdout.write(line)
