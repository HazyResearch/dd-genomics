#!/usr/bin/env python

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
        is_correct = None
        if rv == True:
          is_correct = 't'
        if rv == False:
          is_correct = 'f'
        print '%s\t%s\t%s\t%s' % (key, is_correct, labeler,version)
