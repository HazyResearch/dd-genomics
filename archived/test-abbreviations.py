#! /usr/bin/env python

'''
Created on Aug 3, 2015

@author: jbirgmei
'''

import abbreviations

if __name__ == '__main__':
  sentence = 'Scaffold proteins are abundant and essential components of the postsynaptic density -LRB- PSD -RRB- as well as I Hate JavaScript Proteins -LRB- IHJSP -RRB- , and a completely unrelated parenthesis -LRB- THIS -RRB- and a definition that could maybe fit but is way too long -LRB- AA -RRB- .'.split(' ')
  print abbreviations.getabbreviations(sentence)
  sentence = 'This sentence certainly contains no parentheses .'.split()
  print abbreviations.getabbreviations(sentence);
  sentence = 'This sentence is botched -RRB- asdf -LRB-'.split()
  print abbreviations.getabbreviations(sentence)
  sentence = 'This sentence is botched -LRB- IB'.split()
  print abbreviations.getabbreviations(sentence)
  sentence = 'While|^|the|^|intestinal|^|stem|^|cells|^|-LRB-|^|ISCs|^|-RRB-|^|are|^|essential|^|for|^|the|^|proliferative|^|aspects|^|of|^|intestinal|^|homeostasis|^|--|^|,|^|the|^|enterocytes|^|-LRB-|^|ECs|^|-RRB-|^|form|^|the|^|first|^|line|^|of|^|defence|^|against|^|pathogens|^|and|^|stressors|^|.'.split('|^|')
  print abbreviations.getabbreviations(sentence)
