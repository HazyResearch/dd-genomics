#! /usr/bin/env python

import json
import sys
import os.path


# get the labeling version number
version = 0 # in case the file doesn't exist
if os.path.exists('version_labeling'):
  with open('version_labeling') as f:
    for i, line in enumerate(f):
      if i == 0:
        version = line[0].strip()
else:
  print 'version_labeling file doesn\'t exist'
  print 'setting version to 0'

if __name__ == "__main__":
  tags_file = sys.argv[1]
  labeler = sys.argv[2]
  with open(tags_file) as t:
    results = json.load(t)
  for key in results['by_key']:
    if 'is_correct' in results['by_key'][key]:
      rv = results['by_key'][key]['is_correct']
      type_value = None
      if u'Causation' in results['by_key'][key]:
        val = results['by_key'][key]['Causation']
        if val == True:
          type_value = None
          rv = False
      elif u'Association' in results['by_key'][key]:
        val = results['by_key'][key]['Association']
        if val == True:
          type_value = 'association'
      elif u'causation' in results['by_key'][key]:
        val = results['by_key'][key]['causation']
        if val == True:
          type_value = None
          rv = False
      elif u'association' in results['by_key'][key]:
        val = results['by_key'][key]['association']
        if val == True:
          type_value = 'association'
      is_correct = None
      if rv == True:
        is_correct = 't'
      if rv == False:
        is_correct = 'f'
      if is_correct == 't':
        if type_value is not None:
          print '%s\t%s\t%s\t%s' % (key, is_correct, labeler, version)
      elif is_correct == 'f':
        print '%s\t%s\t%s\t%s' % (key, is_correct, labeler, version)
