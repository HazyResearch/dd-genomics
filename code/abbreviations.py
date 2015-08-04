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
  if '-LRB-' in sentence:
    # Check some things first
    if sentence.count('-LRB-') != sentence.count('-RRB-'):
      raise ValueError('Unbalanced parentheses: %s' % sentence)

    if sentence.index('-LRB-') > sentence.index('-RRB-'):
      raise ValueError('First parentheses is right: %s' % sentence)

    closeindex = -1
    openindex = len(sentence)
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
      str = sentence[start:stop]

      if conditions(str):
        yield (start, stop, str)


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
  
  str = ' '.join(str)
  
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


def getdefinition((startAbbrev, stopAbbrev, abbrev), sentence):
  ':type candidate: (int, int, list[str])'
  ':type sentence: list[str]'
  '''Takes a candidate and a sentence and returns the definition candidate.

  The definition candidate is the set of tokens (in front of the candidate)
  that starts with a token starting with the first character of the candidate'''
  # Take the tokens in front of the candidate
  tokens = [word.lower() for word in sentence[:startAbbrev - 1]]
  print tokens
  print len(tokens)

  # the char that we are looking for
  key = abbrev[0][0].lower()

  # Count the number of tokens that start with the same character as the
  # candidate
  firstchars = [t[0] for t in tokens]

  definitionfreq = firstchars.count(key)
  candidatefreq = ' '.join(abbrev).lower().count(key)

  # Look for the list of tokens in front of candidate that
  # have a sufficient number of tokens starting with key
  if candidatefreq <= definitionfreq:
    startDefinition = 0
    stopDefinition = startAbbrev - 1
    definitionStr = sentence[startDefinition:stopDefinition]
    return (0, stopDefinition, definitionStr)

  else:
    raise ValueError(
      'There are fewer keys in the tokens in front of candidate than there are in the candidate')


def definitionselection(definition, abbrev):
  '''Takes a definition candidate and an abbreviation candidate
  and returns True if the chars in the abbreviation occur in the definition

  Based on 
  A simple algorithm for identifying abbreviation definitions in biomedical texts, Schwartz & Hearst'''

  if abbrev in definition[2]:
    raise ValueError('Abbreviation is full word of definition')

  print definition[2]
  definitionStr = ' '.join(definition[2])
  print definitionStr
  assert len(abbrev[2]) == 1;
  abbrev = abbrev[2][0]

  if len(definitionStr) < len(abbrev):
    raise ValueError('Abbreviation is longer than definition')

  sindex = -1
  lindex = -1
  stopDefinition = definition[1]
  startDefinition = stopDefinition - 1
  print startDefinition, stopDefinition

  while 1:
    if definitionStr[lindex] == ' ':
      startDefinition -=1
      lindex -= 1
      continue
    
    try:
      longchar = definitionStr[lindex].lower()
    except IndexError:
      # print definitionStr, '||',abbrev
      raise

    shortchar = abbrev[sindex].lower()

    if not shortchar.isalnum():
      sindex -= 1

    if sindex == -1 * len(abbrev):
      if shortchar == longchar:
        if lindex == -1 * len(definitionStr) or not definitionStr[lindex - 1].isalnum():
          break
        else:
          lindex -= 1
      else:
        lindex -= 1

        if lindex == -1 * (len(definitionStr) + 1):
          raise ValueError(
            'definition of "%s" not found in "%s"' % (abbrev, definitionStr))

    else:
      if shortchar == longchar:
        sindex -= 1
        lindex -= 1
      else:
        lindex -= 1

  definition = (startDefinition, stopDefinition, definition[2][startDefinition:stopDefinition])

  tokens = len(definition)
  length = len(abbrev)

  if tokens > min([length + 5, length * 2]):
    raise ValueError('did not meet min(|A|+5, |A|*2) constraint (%d, %d)' % (tokens, length))

  # Do not return definitions that contain unbalanced parentheses
  if not __REPRODUCE__:
    if definition.count('(') != definition.count(')'):
      raise ValueError(
        'Unbalanced parentheses not allowed in a definition')

  return definition

def getabbreviations(sentence):
  rv = []
  for abbrev in getcandidates(sentence):
    try:
      definition = getdefinition(abbrev, sentence)
      print "Definition2: " + str(definition)
    except ValueError, e:
      print >> sys.stderr, 'Omitting abbreviation candidate', abbrev
      print >> sys.stderr, 'Reason:', e.args[0], '\n'
    else:
      try:
        definition = definitionselection(definition, abbrev)
      except ValueError, e:
        # print >>sys.stderr, i, sentence
        print >> sys.stderr, 'Omitting abbreviation candidate', definition, '||', definition
        print >> sys.stderr, 'Reason:', e.args[0], '\n'
      else:
        rv.append((abbrev, definition))
  return rv
