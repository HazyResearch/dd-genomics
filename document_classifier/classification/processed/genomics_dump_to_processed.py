#! /usr/bin/env python

import sys
import re

if __name__ == "__main__":
  no_alnum = re.compile(r'[\W_]+')
  with open(sys.argv[2], 'w') as out_file:
    with open(sys.argv[1]) as f:
      for line in f:
        comps = line.strip().split('\t')
        pmid = comps[0]
        journal = comps[1]
        mesh_terms_string = comps[2]
        sv = comps[3]
        text = comps[4]
        gm = comps[5]
        pm = comps[6]
  
        sentences = text.split('|~^~|')
        gm_sentences = gm.split('|~^~|')
        pm_sentences = pm.split('|~^~|')
        mesh_terms = mesh_terms_string.split('|^|')
  
        new_text = 'JOURNAL_' + no_alnum.sub('_', journal).strip() + ' ' + ' '.join(['MeSH_' + no_alnum.sub('_', x).strip() for x in mesh_terms]) + ' '
        for i, sentence in enumerate(sentences):
          words = sentence.split('|^|')
          if i >= len(gm_sentences):
            print >>sys.stderr, (pmid, i, gm_sentences)
          gms_string = gm_sentences[i]
          pms_string = pm_sentences[i]
          if gms_string != 'N':
            gms = gms_string.split('|^+^|')
            for gm in [int(x) for x in gms]:
              words[gm] = 'ENSEMBLGENE'
          if pms_string != 'N':
            pms = pms_string.split('|^+^|')
            for pm in [int(x) for x in pms]:
              words[pm] = 'DETECTEDPHENO'
          new_text += ' ' + ' '.join(words)
        print >>out_file, "%s\t%s\t%s" % (pmid, new_text, sv)
