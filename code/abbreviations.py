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


encoding = 'UTF8'


def fread(fname, encoding=encoding):
  f = open(os.path.abspath(os.path.expanduser(fname)))
  try:
    for l in f:
      line = l.strip()
      if line:
        yield line.decode(encoding)
  finally:
    f.close()


def fread2(fname, encoding=encoding):
  f = open(os.path.abspath(os.path.expanduser(fname)))
  try:
    for l in f:
      line = l.strip().decode(encoding)
      if line:
        yield line.split()
      else:
        yield None
  finally:
    f.close()


class Candidate(unicode):

  def __new__(cls, start, stop, str):
    return unicode.__new__(cls, str)

  def __init__(self, start, stop, str):
    self._start = start
    self._stop = stop

  def __getslice__(self, i, j):
    start = self.start + i
    stop = self.start + j
    str = unicode.__getslice__(self, i, j)
    return Candidate(start, stop, str)

  @property
  def start(self):
    '''The start index'''
    return self._start

  @property
  def stop(self):
    '''The stop index'''
    return self._stop


def getcandidates(sentence):
  '''Yields Candidates'''
  if '-LRB-' in sentence:
    # Check some things first
    if sentence.count('-LRB-') != sentence.count('-RRB-'):
      raise ValueError('Unbalanced parentheses: %s' % sentence)

    if sentence.find('-LRB-') > sentence.find('-RRB-'):
      raise ValueError('First parentheses is right: %s' % sentence)

    closeindex = -1
    while 1:
      # Look for open parenthesis
      openindex = sentence.find('-LRB-', closeindex + 1)

      if openindex == -1:
        break

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
      str = ' '.join(sentence[start:stop])

      if conditions(str):
        yield Candidate(start, stop, str)


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


def getdefinition(candidate, sentence):
  '''Takes a candidate and a sentence and returns the definition candidate.

  The definition candidate is the set of tokens (in front of the candidate)
  that starts with a token starting with the first character of the candidate'''
  # Take the tokens in front of the candidate
  tokens = sentence[:candidate.start - 1].lower()

  # the char that we are looking for
  key = candidate[0].lower()

  # Count the number of tokens that start with the same character as the
  # candidate
  firstchars = [t[0] for t in tokens]

  definitionfreq = firstchars.count(key)
  candidatefreq = candidate.lower().count(key)

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
    start = len(' '.join(tokens[:startindex]))
    stop = candidate.start - 2
    str = sentence[start:stop]

    # Remove whitespace
    start = start + len(str) - len(str.lstrip())
    stop = stop - len(str) + len(str.rstrip())
    str = sentence[start:stop]

    return Candidate(start, stop, str)

  else:
    # print 'S', sentence
    # print >>sys.stderr, 'KEY', key
    # print >>sys.stderr, 'TOKENS', tokens
    # print >>sys.stderr, 'ABBREV', candidate
    raise ValueError(
      'There are less keys in the tokens in front of candidate than there are in the candidate')


def definitionselection(definition, abbrev):
  '''Takes a definition candidate and an abbreviation candidate
  and returns True if the chars in the abbreviation occur in the definition

  Based on 
  A simple algorithm for identifying abbreviation definitions in biomedical texts, Schwartz & Hearst'''

  if len(definition) < len(abbrev):
    raise ValueError('Abbreviation is longer than definition')

  if abbrev in definition.split():
    raise ValueError('Abbreviation is full word of definition')

  sindex = -1
  lindex = -1

  while 1:
    try:
      longchar = definition[lindex].lower()
    except IndexError:
      # print definition, '||',abbrev
      raise

    shortchar = abbrev[sindex].lower()

    if not shortchar.isalnum():
      sindex -= 1

    if sindex == -1 * len(abbrev):
      if shortchar == longchar:
        if lindex == -1 * len(definition) or not definition[lindex - 1].isalnum():
          break
        else:
          lindex -= 1
      else:
        lindex -= 1

        if lindex == -1 * (len(definition) + 1):
          raise ValueError(
            'definition of "%s" not found in "%s"' % (abbrev, definition))

    else:
      if shortchar == longchar:
        sindex -= 1
        lindex -= 1
      else:
        lindex -= 1

  definition = definition[lindex:len(definition)]

  tokens = len(definition.split())
  length = len(abbrev)

  if tokens > min([length + 5, length * 2]):
    raise ValueError('did not meet min(|A|+5, |A|*2) constraint')

  # Do not return definitions that contain unbalanced parentheses
  if not __REPRODUCE__:
    # print 'ccc', abbrev, definition, definition.count('('),
    # definition.count(')')
    if definition.count('(') != definition.count(')'):
      raise ValueError(
        'Unbalanced parentheses not allowed in a definition')

  return definition


def main(fname, verbose=False, encoding=encoding):
  '''Writes a file (fname.abb) containing all abbreviations and their definitions in the format

  sentenceindex startindex stopindex abbrev 
  sentenceindex startindex stopindex definition

  sentenceindex startindex stopindex abbrev 
  sentenceindex startindex stopindex definition
  ...


  fname: single-whitespaced tokenized sentences; every sentence on a newline


  Evaluation
  abbreviations.score('abbrev.txt.gold', 'abbrev.txt.raw.abb')

  TP: 673
  FP: 94
  FN: 280

  P : 87.74
  R : 70.62
  F1: 78.26


  abbrev.txt.gold: all gold links in yeast_abbrev_labeled.txt (but as corrected in abbrev.txt)
  abbrev.txt.raw.abb: all links based on abbrev.txt.raw and extractedwith main()
  abbrev.txt: the sentences from yeast_abbrev_labeled.txt with at least one (; tokenized with tokenizer.py and corrected.
  '''
  # name = fname+'.abb'
  # o = open(name, 'w')

  omit = 0
  written = 0
  try:
    for i, sentence in enumerate(fread(fname)):
      try:
        for candidate in getcandidates(sentence):
          try:
            definition = getdefinition(candidate, sentence)
          except ValueError, e:
            # print >>sys.stderr, i, sentence
            if verbose:
              print >> sys.stderr, i, 'Omitting candidate', candidate.encode(
                encoding)
              print >> sys.stderr, 'Reason:', e.args[
                0].encode(encoding), '\n'
            omit += 1
          else:
            try:
              definition = definitionselection(
                definition, candidate)
            except IndexError:
              if verbose:
                # print >>sys.stderr, i, sentence
                print >> sys.stderr, i, 'Omitting candidate', definition.encode(
                  encoding), '||', candidate.encode(encoding), '\n'
              omit += 1
            except ValueError, e:
              if verbose:
                # print >>sys.stderr, i, sentence
                print >> sys.stderr, i, 'Omitting candidate', definition.encode(
                  encoding), '||', candidate.encode(encoding)
                print >> sys.stderr, 'Reason:', e.args[
                  0].encode(encoding), '\n'
              omit += 1
            else:
              # o.write('%d %d %d %s\n' %(i, candidate.start, candidate.stop, candidate))
              # o.write('%d %d %d %s\n' %(i, definition.start, definition.stop, definition))
              # o.write('\n')

              cline = '%d %d %d %s' % (
                i, candidate.start, candidate.stop, candidate)
              dline = '%d %d %d %s' % (
                i, definition.start, definition.stop, definition)

              print cline.encode(encoding)
              print dline.encode(encoding)
              print

              written += 1
      except ValueError, e:
        if verbose:
          # print >>sys.stderr, 'SENTENCE %d:' %i, sentence.encode(encoding)
          # print >>sys.stderr, 'ERROR:', e.args
          print >> sys.stderr, 'Reason:', e.args[
            0].encode(encoding), '\n'

  finally:
    1
    # o.close()

  print >> sys.stderr, 'INFO: %d abbreviations detected and kept (%d omitted)' % (
    written, omit)

  # print >>sys.stderr, 'Written', name




def score(gold, pred):
  '''
  gold: a file as created with extract.write()
  pred: a file as created with main()

  Prints the resulst'''
  golds = {}
  s = []
  for line in fread2(gold):
    if line:
      s.append(' '.join(line[1:]))
      id = line[0]
    elif s:
      golds[id] = golds.get(id, []) + [tuple(s)]
      s = []

  preds = {}
  s = []
  for line in fread2(pred):
    if line:
      s.append(' '.join(line[3:]))
      id = line[0]
    elif s:
      preds[id] = preds.get(id, []) + [tuple(s)]
      s = []

  tp = 0
  fp = 0
  fn = 0
  for id, gvalues in golds.items():
    for pair in gvalues:
      try:
        pvalues = preds[id]
      except KeyError:
        fn += 1
      else:
        if pair in pvalues:
          tp += 1
          preds[id].remove(pair)
        else:
          print 'false negative', id, pair
          fn += 1

  for id, pvalues in preds.items():
    fp += len(pvalues)

  # The number of gold abbreviatios
  total = 0
  for v in golds.values():
    total += len(v)

  print '''
TP: %d
FP: %d
FN: %d

P : %5.2f
R : %5.2f
F1: %5.2f

In total there were %d gold definition/abbreviation pairs.

''' % (tp, fp, fn, precision(tp, fp), recall(tp, fn), fscore(tp, fp, fn), total)


def recall(TP, FN):
  if TP == 0:
    return 0
  return 100 * float(TP) / (TP + FN)


def precision(TP, FP):
  if TP == 0:
    return 0
  return 100 * float(TP) / (TP + FP)


def fscore(TP, FP, FN):
  R = recall(TP, FN)
  P = precision(TP, FP)

  if R == 0 or P == 0:
    return 0

  return 2 * R * P / (R + P)


def _usage():
  print >> sys.stderr, __doc__

def getabbreviations(sentence):
  rv = []
  for candidate in getcandidates(sentence):
    try:
      definition = getdefinition(candidate, sentence)
    except ValueError, e:
      if verbose:
        print >> sys.stderr, 'Omitting abbreviation candidate', candidate.encode(
          encoding)
        print >> sys.stderr, 'Reason:', e.args[
          0].encode(encoding), '\n'
    else:
      try:
        definition = definitionselection(
          definition, candidate)
      except IndexError:
        if verbose:
          print >> sys.stderr, 'Omitting abbreviation candidate', definition.encode(
            encoding), '||', candidate.encode(encoding), '\n'
      except ValueError, e:
        if verbose:
          # print >>sys.stderr, i, sentence
          print >> sys.stderr, 'Omitting abbreviation candidate', definition.encode(
            encoding), '||', candidate.encode(encoding)
          print >> sys.stderr, 'Reason:', e.args[
            0].encode(encoding), '\n'
      else:
        rv.append((candidate.start, candidate.stop, candidate, definition))
  return rv

if __name__ == '__main__':
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hv', ['help'])
  except getopt.GetoptError:
    # print help information and exit:
    _usage()
    sys.exit(2)

  verbose = False

  for o, a in opts:
    if o in ('-h', '--help'):
      _usage()
      sys.exit()
    if o == '-v':
      verbose = True

  if len(args) != 1:
    _usage()
    sys.exit(1)

  main(args[0], verbose=verbose)
