#! /usr/bin/env python

import fileinput

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
    if len(comps) == 1:
      pmid = comps[0]
      source_name = 'null'
      year = 2100
      text_year = 'null'
      year_status = 'null'
    elif len(comps) == 2:
      pmid = comps[0]
      source_name = comps[1]
      year = 2100
      text_year = 'null'
      year_status = 'null'
    elif len(comps) == 3:
      text_year = comps[2].strip()
      pmid = comps[0]
      source_name = comps[1]

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
      assert False, comps

    print '%s\t%s\t%s\t%s\t%s' % (pmid, source_name, year, text_year, year_status)
