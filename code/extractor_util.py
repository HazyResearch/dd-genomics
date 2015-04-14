"""Miscellaneous shared tools for extractors."""
from collections import namedtuple
import os

CODE_DIR = os.path.dirname(os.path.realpath(__file__))
APP_HOME = os.path.dirname(CODE_DIR)


Sentence = namedtuple(
    'Sentence', ['doc_id', 'sent_id', 'words', 'poses', 'ners', 'lemmas'])


Mention = namedtuple(
    'Mention', ['dd_id', 'doc_id', 'sent_id', 'wordidxs', 'mention_id',
                'mention_type', 'entity', 'words', 'is_correct'])


def create_mention(sentence, wordidxs, words, entity, mention_type=None, is_correct=None):
  """Create a mention (unary) record"""
  mention_id = '%s_%s_%s_%s' % (sentence.doc_id, sentence.sent_id, wordidxs[0], wordidxs[-1])
  if mention_type:
    mention_id = '%s_%s' % (mention_id, mention_type)
  return Mention(dd_id=None,
                 doc_id=sentence.doc_id,
                 sent_id=sentence.sent_id,
                 wordidxs=wordidxs,
                 mention_id=mention_id,
                 mention_type=mention_type,
                 entity=entity,
                 words=words,
                 is_correct=is_correct)


def list_to_pg_array(l):
  """Convert a list to a string that PostgreSQL's COPY FROM understands."""
  return '{%s}' % ','.join(str(x) for x in l)


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

  
def tsv_string_to_list(s, func=None, sep='|^|'):
  """Convert a TSV string from the sentences_input table to a list

  Args:
    s: String to transform
    func: Apply this function to each element in the resultin list.
       e.g. pass int to convert everything to ints automatically.
    sep: The delimiter used in s.
  Returns:
    list of elements.
  """
  if func is None:
    func = lambda x: x
  return [func(x) for x in s.split(sep)]
