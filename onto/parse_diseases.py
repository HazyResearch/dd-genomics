#! /usr/bin/env python

from xml.etree.ElementTree import ElementTree
import sys
import re

def attach_diseases(diseases):
  ret = []
  for line in diseases.split('\n'):
    names = line.strip().split(';')
    for name in names:
      if name.strip():
        ret.append(re.sub(r'\W+', ' ', name.strip()))
  return ret

if __name__ == "__main__":
  filename = sys.argv[1]
  doc = ElementTree(file=filename)
  e = doc.findall('.//mimNumber')[0]
  mimNumber = e.text
  names = []
  altNames = []
  for e in doc.findall('.//preferredTitle'):
    names += attach_diseases(e.text)
  for e in doc.findall('.//alternativeTitles'):
    altNames += attach_diseases(e.text)
  print "%s\t%s\t%s" % (mimNumber, '|^|'.join(names), '|^|'.join(altNames))
