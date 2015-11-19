#! /usr/bin/env python

import sys

if __name__ == "__main__":
  cur_pmid = -1
  cur_str = ''
  for line in sys.stdin:
    comps = line.strip().split('\t')
    pmid = int(comps[0])
    if pmid == cur_pmid:
      cur_str += ' '
      cur_str += comps[1]
    else:
      if cur_pmid != -1:
        print "%s\t%s" % (cur_pmid, cur_str)
      cur_pmid = pmid
      cur_str = comps[1]
  if cur_pmid != -1:
    print "%s\t%s" % (cur_pmid, cur_str)
