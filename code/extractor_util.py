"""Miscellaneous shared tools for extractors."""
from collections import defaultdict, namedtuple
import os
import re
import sys
import ddlib

def rgx_comp(strings=[], rgxs=[]):
  r = r'|'.join(re.escape(w) for w in strings)
  if len(rgxs) > 0:
    if len(strings) > 0:
      r += r'|'
    r += r'(' + r')|('.join(rgxs) + r')'
  return r

def rgx_mult_search(strings=[], rgxs=[], phrase, flags=re.I):
  for s in strings:
    regex = re.escape(s)
    if re.search(regex, phrase, flags):
      return s
  for s in rgxs:
    regex = s
    if re.search(regex, phrase, flags):
      return s
  return None

# HACK[Alex]: this is probably justified but a bit hackey still...
def skip_row(row):
  """
  Filter sentences dynamically which we want to skip for now uniformly across all extractors
  NOTE: could do this as preprocessing step but since this is a bit of a hack should be more
  transparent...
  Assumes Row object has words, poses attributes
  """

  # Hack[Alex]: upper limit for sentences, specifically to deal w preprocessing errors
  if len(row.words) > 90:
    return True

  # Require that there is a verb in the sentence
  if not any(pos.startswith("VB") for pos in row.poses):
    return True

  # Filter out by certain specific identifying tokens
  exclude_strings = ['http://', 'https://']
  exclude_patterns = ['\w+\.(com|org|edu|gov)']
  for ex in [re.escape(s) for s in exclude_strings] + exclude_patterns:
    for word in row.words:
      if re.search(ex, word, re.I|re.S):
        return True
  return False

APP_HOME = os.environ['GDD_HOME']

def print_error(err_string):
  """Function to write to stderr"""
  sys.stderr.write("ERROR[UDF]: " + str(err_string) + "\n")

def tsv_string_to_list(s, func=lambda x : x, sep='|^|'):
  """Convert a TSV string from the sentences_input table to a list,
  optionally applying a fn to each element"""

  # Auto-detect separator
  if re.search(r'^\{|\}$', s):
    split = re.split(r'\s*,\s*', re.sub(r'^\{\s*|\s*\}$', '', s))
  else:
    split = s.split(sep)

  # split and apply function
  return [func(x.strip()) for x in split]


def tsv_string_to_listoflists(s, func=lambda x : x, sep1='|~|', sep2='|^|'):
  """Convert a TSV string from sentences_input table to a list of lists"""
  return tsv_string_to_list(s, func=lambda x : tsv_string_to_list(x, func=func, sep=sep2), sep=sep1)

class Row:
  def __str__(self):
    return '<Row(' + ', '.join("%s=%s" % x for x in self.__dict__.iteritems()) + ')>'
  def __repr__(self):
    return str(self)

def bool_parser(b):
  if b == 't':
    return True
  elif b == 'f':
    return False
  elif b == 'NULL' or b == '\\N':
    return None
  else:
    raise Exception("Unrecognized bool type in RowParser:bool_parser: %s" % b)

# NOTE: array_to_string doesn't work well for bools!  Just pass psql array out!
RP_PARSERS = {
  'text' : lambda x : str(x),
  'text[]' : lambda x : tsv_string_to_list(x),
  'int' : lambda x : int(x),
  'int[]' : lambda x : tsv_string_to_list(x, func=int),
  'int[][]' : lambda x : tsv_string_to_listoflists(x, func=int),
  'boolean' : lambda x : bool_parser(x),
  'boolean[]' : lambda x : tsv_string_to_list(x, func=bool_parser)
}

class RowParser:
  """
  Initialized with a list of duples (field_name, field_type)- see RP_PARSERS dict
  Is a factory for simple Row class parsed from e.g. tsv input lines
  """
  def __init__(self, fields):
    self.fields = fields

  def parse_tsv_row(self, line):
    row = Row()
    cols = line.split('\t')
    for i,col in enumerate(cols):
      field_name, field_type = self.fields[i]
      if RP_PARSERS.has_key(field_type):
        val = RP_PARSERS[field_type](col.strip())
      else:
        raise Exception("Unsupported type %s for RowParser class- please add.")
      setattr(row, field_name, val)
    return row

def create_ddlib_sentence(row):
  """Create a list of ddlib.Word objects from input row."""
  sentence = []
  for i, word in enumerate(row.words):
    sentence.append(ddlib.Word(
        begin_char_offset=None,
        end_char_offset=None,
        word=word,
        lemma=row.lemmas[i],
        pos=row.poses[i],
        ner=row.ners[i],
        dep_par=row.dep_parents[i],
        dep_label=row.dep_paths[i]))
  return sentence

def pg_array_escape(tok):
  """
  Escape a string that's meant to be in a Postgres array.
  We double-quote the string and escape backslashes and double-quotes.
  """
  return '"%s"' % str(tok).replace('\\', '\\\\').replace('"', '\\\\"')

def list_to_pg_array(l):
  """Convert a list to a string that PostgreSQL's COPY FROM understands."""
  return '{%s}' % ','.join(pg_array_escape(x) for x in l)

def print_tsv_output(out_record):
  """Print a tuple as output of TSV extractor."""
  values = []
  for x in out_record:
    if isinstance(x, list) or isinstance(x, tuple):
      cur_val = list_to_pg_array(x)
    elif x is None:
      cur_val = '\N'
    else:
      cur_val = x
    values.append(cur_val)
  print '\t'.join(str(x) for x in values)

def run_main_tsv(row_parser, row_fn):
  """
  Runs through lines in sys.stdin, applying row_fn(row_parser(line))
  Assumes that this outputs a list of rows, which get printed out in tsv format
  Has standard error handling for malformed rows- optimally row_fn returns object with pretty print
  """
  lines_out = []
  for line in sys.stdin:
    row = row_parser(line)
    try:
      lines_out += row_fn(row)
    
    # A malformed input line will often mess up the word indexing...
    except IndexError:
      print_error("Error with row: %s" % (row,))

  for line in lines_out:
    print_tsv_output(line)
