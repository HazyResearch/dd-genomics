#!/usr/bin/env python
'''Link abbreviations to their full names

Based on

A Simple Algorithm for Identifying Abbreviations Definitions in Biomedical Text
A. Schwartz and M. Hearst
Biocomputing, 2003, pp 451-462.


# License: GNU General Public License, see http://www.clips.ua.ac.be/~vincent/scripts/LICENSE.txt
'''
__date__ = 'July 2012'
__author__ = 'Vincent Van Asch'
__version__ = '1.2.1'


# If you want to use the script that produces the results reported in __doc__
# you have to set the global __REPRODUCE__ to True. It is assumed that
# the extra code that is active when __REPRODUCE__ is set to True produces
# better results.
__REPRODUCE__ = False


__doc__ = '''
This script takes tokenized sentences and prints the abbreviations and their definitions to STDOUT.

USAGE
  python [-v] abbreviations.py inputfile > abbreviations
  
FORMATS
  inputfile: A tokenized sentence on every new line (tokens should be separated by a single space)
  abbreviations: 
  sentenceid1 characteroffset_begin_a1 characteroffset_end_a1 abbreviation1
  sentenceid1 characteroffset_begin_d1 characteroffset_end_d1 definition1
  
  sentenceid2 characteroffset_begin2 characteroffset_end2 abbreviation2
  sentenceid2 characteroffset_begin2 characteroffset_end2 definition2
  ...
  
  sentenceid: the line on which the sentence is in the inputfile minus one
  
OPTIONS
  -v: Print more information to STDERR
  
REMARKS
  The algorithm detects only links between an abbreviation and its definition if they
  are in the format <definition> (<abbreviation>). So, the reverse 
  <abbreviation> (<definition>) is not detected.
  
  The algorithm can only find definitions that have all characters of the abbreviation
  in them.
  
  It will also make errors in cases like "tyrosine transcription factor I (TTFI)" 
  the wrong definition will be "transcription factor I" because all characters from
  the abbreviation are in the definition.
  
  On the labeled yeast corpus (http://biotext.berkeley.edu/data.html) version 1.0 of this
  script reaches:
  
  TP: 673
  FP: 94
  FN: 280

  P : 87.74
  R : 70.62
  F1: 78.26
  
  (The corpus had to be corrected manually in order to be useable.)
   
ACKNOWLEDGEMENTS
  Based on:
  A Simple Algorithm for Identifying Abbreviations Definitions in Biomedical Text
  A. Schwartz and M. Hearst
  Biocomputing, 2003, pp 451-462.

%s (version %s)''' % (__date__, __version__)

import os
import sys
import re
import getopt


def getcandidates(sentence):
  '''Yields Candidates'''
  rv = []
  if '-LRB-' in sentence:
    # Check some things first
    if sentence.count('-LRB-') != sentence.count('-RRB-'):
      raise ValueError('[NO_SUP] Unbalanced parentheses: %s' % sentence)

    try:
      lrbIndex = sentence.index('-LRB-')
    except ValueError:
      lrbIndex = -1
    try:
      rrbIndex = sentence.index('-RRB-')
    except ValueError:
      rrbIndex = -1
    print lrbIndex, rrbIndex
    if lrbIndex > rrbIndex:
      raise ValueError('[NO_SUP] First parentheses is right: %s' % sentence)

    closeindex = -1
    while 1:
      # Look for open parenthesis
      try:
        openindex = closeindex + 1 + sentence[closeindex + 1:].index('-LRB-')
      except ValueError:
        break;

      # Look for closing parentheses
      closeindex = openindex + 1
      open = 1
      skip = False
      while open:
        try:
          char = sentence[closeindex]
        except IndexError:
          # We found an opening bracket but no associated closing bracket
          # Skip the opening bracket
          skip = True
          break
        if char == '-LRB-':
          open += 1
        elif char == '-RRB-':
          open -= 1
        closeindex += 1

      if skip:
        closeindex = openindex + 1
        continue

      # Output if conditions are met
      start = openindex + 1
      stop = closeindex - 1
      assert stop == start + 1
      str = sentence[start]

      if conditions(str):
        rv.append((start, stop, str))
  return rv


def conditions(str):
  '''Based on Schwartz&Hearst

  2 <= len(str) <= 10
  len(tokens) <= 2
  re.search('[A-Za-z]', str)
  str[0].isalnum()

  and extra:
  if it matches ([A-Za-z]\. ?){2,}
  it is a good candidate.

  '''

  if not __REPRODUCE__ and re.match('([A-Za-z]\. ?){2,}', str.lstrip()):
    return True
  if len(str) < 2 or len(str) > 10:
    return False
  if len(str.split()) > 2:
    return False
  if not re.search('[A-Za-z]', str):
    return False
  if not str[0].isalnum():
    return False

  return True


def getdefinition((startAbbrev, stopAbbrev, abbrev), sentence, stopLastAbbrev):
  ':type candidate: (int, int, list[str])'
  ':type sentence: list[str]'
  '''Takes a candidate and a sentence and returns the definition candidate.

  The definition candidate is the set of tokens (in front of the candidate)
  that starts with a token starting with the first character of the candidate'''
  startTokens = stopLastAbbrev + 1;
  # Take the tokens in front of the candidate
  tokens = [word.lower() for word in sentence[startTokens:startAbbrev - 1]]
  print "tokens:"
  print tokens

  # the char that we are looking for
  key = abbrev[0].lower()

  # Count the number of tokens that start with the same character as the
  # candidate
  firstchars = [t[0] for t in tokens]

  definitionfreq = firstchars.count(key)
  candidatefreq = abbrev.lower().count(key)

  # Look for the list of tokens in front of candidate that
  # have a sufficient number of tokens starting with key
  if candidatefreq <= definitionfreq:
    # we should at least have a good number of starts
    count = 0
    start = 0
    startindex = len(firstchars) - 1
    while count < candidatefreq:
      if abs(start) > len(firstchars):
        raise ValueError('not found')

      start -= 1
      # Look up key in the definition
      try:
        startindex = firstchars.index(key, len(firstchars) + start)
      except ValueError:
        pass

      # Count the number of keys in definition
      count = firstchars[startindex:].count(key)

    # We found enough keys in the definition so return the definition as a
    # definition candidate
    str = sentence[startindex + startTokens:startAbbrev - 1]
    rv = (startindex + startTokens, startAbbrev - 1, str)
    return rv

  else:
    raise ValueError(
      '[SUP] There are fewer keys in the tokens in front of candidate than there are in the candidate')


def definitionselection((startDefinition, stopDefinition, definition), (startAbbrev, stopAbbrev, abbrev)):
  '''Takes a definition candidate and an abbreviation candidate
  and returns True if the chars in the abbreviation occur in the definition

  Based on 
  A simple algorithm for identifying abbreviation definitions in biomedical texts, Schwartz & Hearst'''

  if abbrev in definition:
    raise ValueError('[SUP] Abbreviation is full word of definition')

  definitionStr = ' '.join(definition)

  if len(definitionStr) < len(abbrev):
    raise ValueError('[SUP] Abbreviation is longer than definition')

  sIndex = -1
  lWordIndex = -1
  lCharacterIndex = -1

  # find all except the first char of the abbreviation
  newStopDefinition = -1
  while 1:
    shortChar = abbrev[sIndex].lower()
    longChar = definition[lWordIndex][lCharacterIndex].lower()
    
    if shortChar == longChar:
      if stopDefinition == -1:
        stopDefinition = len(definition) + lWordIndex
      sIndex -= 1
    if (lCharacterIndex == -1 * len(definition[lWordIndex])):
      lCharacterIndex = -1
      lWordIndex -= 1
    else:
      lCharacterIndex -= 1

    if lWordIndex == -1 * (len(definition) + 1):
      raise ValueError('[SUP] Cannot find abbreviation in definition')
    if sIndex == -1 * len(abbrev):
      break;
      
  # find the first char of the abbreviation as the first char of a word
  while 1:
    assert sIndex == -1 * len(abbrev)
    shortChar = abbrev[sIndex].lower()
    longChar = definition[lWordIndex][0].lower()
    if shortChar == longChar:
      break;
    lWordIndex -= 1
    if lWordIndex == -1 * (len(definition) + 1):
      raise ValueError('[SUP] Cannot find abbreviation in definition')

  definition = definition[len(definition) + lWordIndex:stopDefinition]
  tokens = len(definition)
  length = len(abbrev)

  if tokens > min([length + 5, length * 2]):
    raise ValueError('[SUP] did not meet min(|A|+5, |A|*2) constraint (%d, %d)' % (tokens, length))

  # Do not return definitions that contain unbalanced parentheses
  if not __REPRODUCE__:
    if definition.count('-LRB-') != definition.count('-RRB-'):
      raise ValueError(
        '[NO_SUP] Unbalanced parentheses not allowed in a definition')

  return (startDefinition, stopDefinition, definition)

def getabbreviations(sentence):
  rv = []
  try:
    abbrevs = getcandidates(sentence)
  except ValueError, e:
    print 'Omitting sentence'
    print 'Reason: %s' % e.args[0]
    return rv

  lastStopAbbreviation = 0
  for abbrev in abbrevs:
    try:
      definition = getdefinition(abbrev, sentence, lastStopAbbreviation)
      print definition
    except ValueError, e:
      print 'Omitting abbreviation candidate %s' % abbrev[2]
      print 'Reason: %s' % e.args[0]
      if e.args[0].startswith('[SUP]'):
        startFakeDefinition = abbrev[0] - 1 - len(abbrev[2])
        stopFakeDefinition = abbrev[0] - 1
        rv.append((False, abbrev, (startFakeDefinition, stopFakeDefinition,
                                 sentence[startFakeDefinition:stopFakeDefinition])))
    else:
      try:
        definition = definitionselection(definition, abbrev)
      except ValueError, e:
        # print >>sys.stderr, i, sentence
        print 'Omitting abbreviation candidate %s' % abbrev[2]
        print 'Reason: %s' % e.args[0]
        if e.args[0].startswith('[SUP]'):
          startFakeDefinition = abbrev[1] - 1 - len(abbrev[2][0])
          stopFakeDefinition = abbrev[1] - 1
          rv.append((False, abbrev, (startFakeDefinition, stopFakeDefinition,
                                 sentence[startFakeDefinition:stopFakeDefinition])))
      else:
        rv.append((True, abbrev, definition))
        lastStopAbbreviation = abbrev[1]
  return rv
