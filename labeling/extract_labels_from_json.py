#!/usr/bin/env python

import json
import sys

if len(sys.argv) != 3:
  print 'Wrong number of arguments'
  print 'USAGE: export_gene_labels.py $DIR/tags.json $LABELER_NAME'
  exit(1)

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
        print '%s\t%s\t%s' % (key, is_correct, labeler)
