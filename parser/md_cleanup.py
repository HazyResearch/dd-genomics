#! /usr/bin/env python

import fileinput
import sys

def getDigits(text):
  c = ''
  for i in text:
    if i.isdigit():
      c += i
  if len(c) > 0:
    return int(c)
  return -1

if __name__ == "__main__":
  for line in fileinput.input():
    comps = line.strip().split('\t')
    if len(comps) == 0:
      continue
    elif len(comps) == 6 or len(comps) == 7:
      text_year = comps[2].strip()
      pmid = comps[0]
      source_name = comps[1]
      issn_global = comps[3]
      issn_print = comps[4]
      issn_electronic = comps[5]
      if len(comps) >= 7:
        mesh_terms = comps[6]
      else:
        mesh_terms = ''

      if pmid == 'null':
        continue
      if text_year == 'null':
        year = 2100
        year_status = 'null'
      elif text_year.isdigit():
        year = int(text_year)
        year_status = 'ok'
      else:
        year = getDigits(text_year)
        if year < 1850:
          year = 2100
          year_status = 'not ok'
        else:
          year_status = 'extracted'
    else:
      print line
      continue

    print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (pmid, source_name, year, text_year, year_status, issn_global, issn_print, issn_electronic, mesh_terms)
