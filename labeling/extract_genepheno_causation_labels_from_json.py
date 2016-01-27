#! /usr/bin/env python

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
      type_value = None
      if u'Association' in results['by_key'][key]:
        val = results['by_key'][key]['Association']
        if val == True:
          type_value = None
          rv = False
      elif u'Causation' in results['by_key'][key]:
        val = results['by_key'][key]['Causation']
        if val == True:
          type_value = 'causation'
      elif u'association' in results['by_key'][key]:
        val = results['by_key'][key]['association']
        if val == True:
          type_value = None
          rv = False
      elif u'causation' in results['by_key'][key]:
        val = results['by_key'][key]['causation']
        if val == True:
          type_value = 'causation'
      is_correct = None
      if rv == True:
        is_correct = 't'
      if rv == False:
        is_correct = 'f'
      if is_correct == 't':
        if type_value is not None:
          print '%s\t%s\t%s' % (key, is_correct, labeler)
      elif is_correct == 'f':
        print '%s\t%s\t%s' % (key, is_correct, labeler)
