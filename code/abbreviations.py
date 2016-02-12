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

def get_candidates(sentence):
  rv = []
  if '-LRB-' in sentence:
    # XXX HACK (?) Johannes
    # The original version checks some sentence properties here first:
    # balanced parentheses and that the first paren is a left one
    # We don't care that much since we only admit one-word abbrevs
    close_idx = -1
    while 1:
      # Look for parenOpen parenthesis
      try:
        open_idx = close_idx + 1 + sentence[close_idx + 1:].index('-LRB-')
      except ValueError:
        break
      close_idx = open_idx + 2
      
      # XXX HACK (?) Johannes
      # The original version picks up acronyms that include parentheses and multiple words.
      # Since there are no such gene abbreviations, such words won't be confused for being 
      # genes anyways, so I just stop after the first word in the parenthesis
      start = open_idx + 1
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

def get_def((start_abbrev, stop_abbrev, abbrev), sentence, stop_last_abbrev):
  ':type candidate: (int, int, list[str])'
  ':type sentence: list[str]'
  start_tokens = stop_last_abbrev + 1
  # Take the tokens in front of the candidate
  tokens = [word.lower() for word in sentence[start_tokens:start_abbrev - 1]]

  # the char that we are looking for
  key = abbrev[0].lower()

  if len(tokens) == 0:
    raise ValueError('[SUP] Not enough keys')

  # Count the number of tokens that start with the same character as the
  # candidate
  first_chars = [t[0] for t in tokens if len(t) > 0]

  def_freq = first_chars.count(key)
  candidate_freq = abbrev.lower().count(key)

  # Look for the list of tokens in front of candidate that
  # have a sufficient number of tokens starting with key
  if candidate_freq <= def_freq:
    # we should at least have a good number of starts
    count = 0
    start = 0
    start_idx = len(first_chars) - 1
    while count < candidate_freq:
      if abs(start) > len(first_chars):
        raise ValueError('not found')

      start -= 1
      # Look up key in the definition
      try:
        start_idx = first_chars.index(key, len(first_chars) + start)
      except ValueError:
        pass

      # Count the number of keys in definition
      count = first_chars[start_idx:].count(key)

    # We found enough keys in the definition so return the definition as a
    # definition candidate
    string = sentence[start_idx + start_tokens:start_abbrev - 1]
    rv = (start_idx + start_tokens, start_abbrev - 1, string)
    return rv

  else:
    raise ValueError(
      '[SUP] Not enough keys')

def def_selection((start_def, stop_def, definition), (start_abbrev, stop_abbrev, abbrev)):
  if abbrev.lower() in [word.lower() for word in definition]:
    raise ValueError('[SUP] Abbrv = full word of def')

  def_str = ' '.join(definition)

  if len(def_str) < len(abbrev):
    raise ValueError('[SUP] Abbrv longer than def')

  s_idx = -1
  l_word_idx = -1
  l_char_idx = -1

  stop_def = -1

  # find all except the first char of the abbreviation
  while 1:
    assert s_idx < 0
    assert s_idx >= -len(abbrev), (s_idx, abbrev)
    short_char = abbrev[s_idx].lower()

    if len(definition) == 0:
      raise ValueError('[SUP] definition candidate is empty')

    assert -l_word_idx <= len(definition), (definition, l_word_idx, len(definition))
    
    if len(definition[l_word_idx]) == 0:
      l_char_idx = -1
      l_word_idx -= 1
      if -l_word_idx >= (len(definition) + 1):
        raise ValueError('[SUP] Abbrv not in def')
      continue

    assert l_word_idx < 0
    assert -l_word_idx <= len(definition), (len(definition), l_word_idx)
    assert l_char_idx < 0
    assert -l_char_idx <= len(definition[l_word_idx]), (len(definition[l_word_idx]), l_char_idx)
    long_char = definition[l_word_idx][l_char_idx].lower()
    
    if short_char == long_char:
      if stop_def == -1:
        stop_def = start_def + len(definition) + l_word_idx + 1
      s_idx -= 1
    if (l_char_idx == -1 * len(definition[l_word_idx])):
      l_char_idx = -1
      l_word_idx -= 1
    else:
      l_char_idx -= 1

    if -l_word_idx >= (len(definition) + 1):
      raise ValueError('[SUP] Abbrv not in def')
    if -s_idx == len(abbrev):
      break;
      
  # find the first char of the abbreviation as the first char of a word
  while 1:
    if len(definition[l_word_idx]) == 0:
      l_word_idx -= 1
      if -l_word_idx >= (len(definition) + 1):
        raise ValueError('[SUP] Abbrv not in def')
    assert s_idx == -1 * len(abbrev)
    short_char = abbrev[s_idx].lower()
    long_char = definition[l_word_idx][0].lower()
    if short_char == long_char:
      break;
    l_word_idx -= 1
    if -l_word_idx >= (len(definition) + 1):
      raise ValueError('[SUP] Abbrv not in def')

  definition = definition[len(definition) + l_word_idx:stop_def]
  tokens = len(definition)
  length = len(abbrev)

  if tokens > min([length + 5, length * 2]):
    raise ValueError('[SUP] length constraint violation')

  # Do not return definitions that contain unbalanced parentheses
  if definition.count('-LRB-') != definition.count('-RRB-'):
    raise ValueError(
      '[SUP] Unbalanced paren in def')

  return (start_def, stop_def, definition)

def getabbreviations(sentence, abbrev_index=None):
  rv = []
  try:
    if not abbrev_index:
      abbrevs = get_candidates(sentence)
    else:
      if conditions(sentence[abbrev_index]):
        abbrevs = [(abbrev_index, abbrev_index+1, sentence[abbrev_index])]
      else:
        abbrevs = []
  except ValueError, e:
    # sys.stderr.write('Abbreviation detection: omitting sentence\n')
    # sys.stderr.write('Reason: %s\n' % e.args[0])
    return rv

  last_stop_abbrev = -1
  for abbrev in abbrevs:
    try:
      definition = get_def(abbrev, sentence, last_stop_abbrev)
      # sys.stderr.write(abbrev[2] + '=' + str(definition) + '\n')
    except ValueError, e:
      # sys.stderr.write('Omitting abbreviation candidate %s\n' % abbrev[2])
      # sys.stderr.write('Reason: %s\n' % e.args[0])
      if e.args[0].startswith('[SUP]'):
        start_fake_def = max(abbrev[0] - 2 - len(abbrev[2]), 0)
        stop_fake_def = abbrev[0] - 2
        rv.append((False, abbrev, (start_fake_def, stop_fake_def,
                                 sentence[start_fake_def:stop_fake_def]), e.args[0]))
    else:
      try:
        definition = def_selection(definition, abbrev)
      except ValueError, e:
        # sys.stderr.write('Omitting abbreviation candidate %s\n' % abbrev[2])
        # sys.stderr.write('Reason: %s\n' % e.args[0])
        if e.args[0].startswith('[SUP]'):
          start_fake_def = max(abbrev[0] - 2 - len(abbrev[2]), 0)
          stop_fake_def = abbrev[1] - 2
          rv.append((False, abbrev, (start_fake_def, stop_fake_def,
                                 sentence[start_fake_def:stop_fake_def]), e.args[0]))
      else:
        rv.append((True, abbrev, definition, ''))
        last_stop_abbrev = abbrev[1]
  return rv
