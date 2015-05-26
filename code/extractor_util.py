"""Miscellaneous shared tools for extractors."""
from collections import defaultdict, namedtuple
import os
import re

CODE_DIR = os.path.dirname(os.path.realpath(__file__))
APP_HOME = os.path.dirname(CODE_DIR)


Sentence = namedtuple(
    'Sentence', ['doc_id', 'sent_id', 'words', 'poses', 'ners', 'lemmas'])


Mention = namedtuple(
    'Mention', ['dd_id', 'doc_id', 'sent_id', 'wordidxs', 'mention_id',
                'mention_type', 'entity', 'words', 'is_correct'])

PLOS_SUBTYPES_TO_DOI_ABBREV = {
    'biol': '10.1371/journal.pbio',
    'clin': '10.1371/journal.pctr',
    'comput': '10.1371/journal.pcbi',
    # Omit PlOS Currents.
    'genet': '10.1371/journal.pgen',
    'med': '10.1371/journal.pmed',
    'negl': '10.1371/journal.pntd',
    'negl': '10.1371/journal.pntd',
    'one': '10.1371/journal.pone',
    'pathog': '10.1371/journal.ppat',
}


class Dag:
  """Class representing a directed acyclic graph."""
  def __init__(self, nodes, edges):
    self.nodes = nodes
    self.node_set = set(nodes)
    self.edges = edges  # edges is dict mapping child to list of parents
    self._has_child_memoizer = defaultdict(dict)

  def has_child(self, parent, child):
    """Check if child is a child of parent."""
    if child not in self.node_set:
      raise ValueError('"%s" not in the DAG.' % child)
    if parent not in self.node_set:
      raise ValueError('"%s" not in the DAG.' % parent)
    if child == parent:
      return True
    if child in self._has_child_memoizer[parent]:
      return self._has_child_memoizer[parent][child]
    for node in self.edges[child]:
      if self.has_child(parent, node):
        self._has_child_memoizer[parent][child] = True
        return True
    self._has_child_memoizer[parent][child] = False
    return False


def read_hpo_dag():
  with open('%s/onto/data/hpo_phenotypes.tsv' % APP_HOME) as f:
    nodes = []
    edges = {}
    for line in f:
      toks = line.strip(' \r\n').split('\t')
      child = toks[0]
      nodes.append(child)
      parents_str = toks[5]
      if parents_str:
        edges[child] = parents_str.split('|')
      else:
        edges[child] = []
    return Dag(nodes, edges)


def get_hpo_phenos(hpo_dag, parent='HP:0000118'):
  """Get only the children of 'Phenotypic Abnormality' (HP:0000118)."""
  return [hpo_term for hpo_term in hpo_dag.nodes
          if hpo_dag.has_child(parent, hpo_term)]



def read_hpo_synonyms():
  syn_dict = dict()
  with open('%s/onto/data/hpo_phenotypes.tsv' % APP_HOME) as f:
    for line in f:
      toks = line.strip(' \r\n').split('\t')
      node = toks[0]
      syn_dict[node] = node
      syn_str = toks[4]
      if syn_str:
        print syn_str
        for syn in syn_str.split('|'):
          syn_dict[syn] = node
  return syn_dict


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


def pg_array_escape(tok):
  """Escape a string that's meant to be in a Postgres array.
  
  We double-quote the string and escape backslashes and double-quotes.
  """
  if isinstance(tok, str):
    escaped = tok.replace('\\', '\\\\').replace('"', '\\"')
    return '"%s"' % escaped
  else:
    return str(tok)

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

  
def tsv_string_to_list(s, func=lambda x : x, sep='|^|'):
  """Convert a TSV string from the sentences_input table to a list

  Args:
    s: String to transform
    func: Apply this function to each element in the resultin list.
       e.g. pass int to convert everything to ints automatically.
    sep: The delimiter used in s.
  Returns:
    list of elements.
  """

  # Auto-detect separator
  if re.search(re.escape(sep), s):
    split = s.split(sep)
  elif re.search(r'^\{|\}$', s):
    split = re.split(r'\s*,\s*', re.sub(r'^\{\s*|\s*\}$', '', s))
  else:
    raise ValueError("Unrecognized tsv list input: %s" % (s,))

  # split and apply function
  return [func(x) for x in split]


def get_pubmed_id_for_doc(doc_id, doi_to_pmid=None):
  """Converts document ID to pubmed ID, or None if not in right format.
  
  doi_to_pmid is optional dict from DOI to PMID, for PLoS documents.
  """
  if '.'.join(doc_id.split('.')[1:]) == "html.txt.nlp.task":
    return doc_id.split('.')[0]

  # PLoS doc IDs look like 'PLoS_One_2010_Dec_14_5(12)_e15617.nxml.txt'
  # Convert to DOI like '10.1371/journal.pone.0015617'
  # Then convert DOI to PMID.
  if doi_to_pmid:
    plos_toks = doc_id.split('_')
    if plos_toks[0] == 'PLoS':
      plos_subtype = plos_toks[1].lower()
      if plos_subtype in PLOS_SUBTYPES_TO_DOI_ABBREV:
        doi_abbrev = PLOS_SUBTYPES_TO_DOI_ABBREV[plos_subtype]
      else:
        return None
      doi_num_match = re.search(r'e([0-9]+)\.nxml\.txt', plos_toks[-1])
      if doi_num_match:
        doi_num = int(doi_num_match.group(1))
      else:
        return None
      doi_id = '%s.%07d' % (doi_abbrev, doi_num)
      if doi_id in doi_to_pmid:
        return doi_to_pmid[doi_id]

  return None


def read_doi_to_pmid():
  """Reads map from DOI to PMID, for PLoS docuemnts."""
  doi_to_pmid = dict()
  with open('%s/onto/data/plos_doi_to_pmid.tsv' % APP_HOME) as f:
    for line in f:
      doi, pmid = line.strip().split('\t')
      doi_to_pmid[doi] = pmid
  return doi_to_pmid
