#!/usr/bin/env python
'''Link abbreviations to their full names

Based on

A Simple Algorithm for Identifying Abbreviations Definitions in Biomedical Text
A. Schwartz and M. Hearst
Biocomputing, 2003, pp 451-462.


# License: GNU General Public License, see http://www.clips.ua.ac.be/~vincent/scripts/LICENSE.txt
'''
__author__ = 'Vincent Van Asch, Johannes Birgmeier'

import re

def getcandidates(sentence):
  rv = []
  if '-LRB-' in sentence:
    # XXX HACK (?) Johannes
    # The original version checks some sentence properties here first:
    # balanced parentheses and that the first paren is a left one
    # We don't care that much since we only admit one-word abbrevs
    closeindex = -1
    while 1:
      # Look for parenOpen parenthesis
      try:
        openindex = closeindex + 1 + sentence[closeindex + 1:].index('-LRB-')
      except ValueError:
        break
      closeindex = openindex + 2
      
      # XXX HACK (?) Johannes
      # The original version picks up acronyms that include parentheses and multiple words.
      # Since there are no such gene abbreviations, such words won't be confused for being 
      # genes anyways, so I just stop after the first word in the parenthesis
      start = openindex + 1
      stop = start + 1
      if start >= len(sentence):
        break
      abbrev = sentence[start]

      if conditions(abbrev):
        rv.append((start, stop, abbrev))
  return rv

def conditions(string):
  if re.match('([A-Za-z]\. ?){2,}', string.lstrip()):
    return True
  if len(string) < 2 or len(string) > 10:
    return False
  if len(string.split()) > 2:
    return False
  if not re.search('[A-Za-z]', string):
    return False
  if not string[0].isalnum():
    return False

  return True

def getdefinition((startAbbrev, stopAbbrev, abbrev), sentence, stopLastAbbrev):
  ':type candidate: (int, int, list[str])'
  ':type sentence: list[str]'
  startTokens = stopLastAbbrev + 1;
  # Take the tokens in front of the candidate
  tokens = [word.lower() for word in sentence[startTokens:startAbbrev - 1]]

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
    string = sentence[startindex + startTokens:startAbbrev - 1]
    rv = (startindex + startTokens, startAbbrev - 1, string)
    return rv

  else:
    raise ValueError(
      '[SUP] Not enough keys')

def definitionselection((startDefinition, stopDefinition, definition), (startAbbrev, stopAbbrev, abbrev)):
  if abbrev.lower() in [word.lower() for word in definition]:
    raise ValueError('[SUP] Abbrv = full word of def')

  definitionStr = ' '.join(definition)

  if len(definitionStr) < len(abbrev):
    raise ValueError('[SUP] Abbrv longer than def')

  sIndex = -1
  lWordIndex = -1
  lCharacterIndex = -1

  stopDefinition = -1

  # find all except the first char of the abbreviation
  while 1:
    shortChar = abbrev[sIndex].lower()
    longChar = definition[lWordIndex][lCharacterIndex].lower()
    
    if shortChar == longChar:
      if stopDefinition == -1:
        stopDefinition = startDefinition + len(definition) + lWordIndex + 1
      sIndex -= 1
    if (lCharacterIndex == -1 * len(definition[lWordIndex])):
      lCharacterIndex = -1
      lWordIndex -= 1
    else:
      lCharacterIndex -= 1

    if lWordIndex == -1 * (len(definition) + 1):
      raise ValueError('[SUP] Abbrv not in def')
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
      raise ValueError('[SUP] Abbrv not in def')

  definition = definition[len(definition) + lWordIndex:stopDefinition]
  tokens = len(definition)
  length = len(abbrev)

  if tokens > min([length + 5, length * 2]):
    raise ValueError('[SUP] length constraint violation')

  # Do not return definitions that contain unbalanced parentheses
  if definition.count('-LRB-') != definition.count('-RRB-'):
    raise ValueError(
      '[SUP] Unbalanced paren in def')

  return (startDefinition, stopDefinition, definition)

def getabbreviations(sentence):
  rv = []
  try:
    abbrevs = getcandidates(sentence)
  except ValueError, e:
    # sys.stderr.write('Abbreviation detection: omitting sentence\n')
    # sys.stderr.write('Reason: %s\n' % e.args[0])
    return rv

  lastStopAbbreviation = 0
  for abbrev in abbrevs:
    try:
      definition = getdefinition(abbrev, sentence, lastStopAbbreviation)
      # sys.stderr.write(abbrev[2] + '=' + str(definition) + '\n')
    except ValueError, e:
      # sys.stderr.write('Omitting abbreviation candidate %s\n' % abbrev[2])
      # sys.stderr.write('Reason: %s\n' % e.args[0])
      if e.args[0].startswith('[SUP]'):
        startFakeDefinition = max(abbrev[0] - 1 - len(abbrev[2]), 0)
        stopFakeDefinition = abbrev[0] - 1
        rv.append((False, abbrev, (startFakeDefinition, stopFakeDefinition,
                                 sentence[startFakeDefinition:stopFakeDefinition]), e.args[0]))
    else:
      try:
        definition = definitionselection(definition, abbrev)
      except ValueError, e:
        # sys.stderr.write('Omitting abbreviation candidate %s\n' % abbrev[2])
        # sys.stderr.write('Reason: %s\n' % e.args[0])
        if e.args[0].startswith('[SUP]'):
          startFakeDefinition = max(abbrev[0] - 1 - len(abbrev[2]), 0)
          stopFakeDefinition = abbrev[1] - 1
          rv.append((False, abbrev, (startFakeDefinition, stopFakeDefinition,
                                 sentence[startFakeDefinition:stopFakeDefinition]), e.args[0]))
      else:
        rv.append((True, abbrev, definition, ''))
        lastStopAbbreviation = abbrev[1]
  return rv
