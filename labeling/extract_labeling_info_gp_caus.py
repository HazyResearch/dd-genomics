#! /usr/bin/env python

import json
import sys

if __name__ == "__main__":
  backup_files = sys.argv[1]
  with open(backup_files) as f:
    for i, line in enumerate(f):
      if i == 0:
        continue
      comps = line.strip().split(';')
      tags_file = comps[0]
      labeler = comps[1]
      with open(tags_file) as t:
        results = json.load(t)
      for key in results['by_key']:
        if 'is_correct' in results['by_key'][key]:
          keyComps = key.split('_')
          (doc_id, section_id, sent_id) = (str(keyComps[0]), str(keyComps[1]), int(keyComps[2]))
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
              print '%s\t%s\t%d\t%s\t%s' % (doc_id, section_id, sent_id, is_correct, labeler)
          elif is_correct == 'f':
            print '%s\t%s\t%d\t%s\t%s' % (doc_id, section_id, sent_id, is_correct, labeler)
