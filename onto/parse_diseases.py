#! /usr/bin/env python

from xml.etree.ElementTree import ElementTree
import sys
import re

def attach_diseases(diseases, excludes):
  excludes = [set(d.strip().split()) for d in excludes]
  for line in diseases.split('\n'):
    names = line.strip().split(';')
    for name in names:
#       if 'GLOMERULOSCLEROSIS' in name:
#         print >> sys.stderr, excludes
#         print >> sys.stderr, set(re.sub(r'\W+', ' ', name.strip()).split(' '))
      if len(name.strip()) > 0 and set(re.sub(r'\W+', ' ', name.strip()).split(' ')) not in excludes:
        yield re.sub(r'\W+', ' ', name.strip())

if __name__ == "__main__":
  filename = sys.argv[1]
  doc = ElementTree(file=filename)
  e = doc.findall('.//mimNumber')[0]
  mim_number = e.text
  names = []
  alt_names = []
  for e in doc.findall('.//preferredTitle'):
    names += attach_diseases(e.text, [])
  for e in doc.findall('.//alternativeTitles'):
    alt_names += attach_diseases(e.text, names)
  print "OMIM:%s\t%s\t%s" % (mim_number, '|^|'.join(names), '|^|'.join(alt_names))
