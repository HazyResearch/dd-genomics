"""Miscellaneous shared tools for maniuplating data used in the UDFs"""
from collections import defaultdict, namedtuple
import extractor_util as util
import os
import re
import sys

APP_HOME = os.environ['GDD_HOME']

onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

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
        for syn in syn_str.split('|'):
          syn_dict[syn] = node
  return syn_dict


def load_pmid_to_hpo():
  """Load map from Pubmed ID to HPO term (via MeSH)"""
  pmid_to_hpo = defaultdict(set)
  with open(onto_path('data/hpo_to_pmid_via_mesh.tsv')) as f:
    for line in f:
      hpo_id, pmid = line.strip().split('\t')
      pmid_to_hpo[pmid].add(hpo_id)
  return pmid_to_hpo


def get_pubmed_id_for_doc(doc_id, doi_to_pmid=None):
  """
  Converts document ID to pubmed ID, or None if not in right format.
  doi_to_pmid is optional dict from DOI to PMID, for PLoS documents.
  """
  if '.'.join(doc_id.split('.')[1:]) == "html.txt.nlp.task":
    return doc_id.split('.')[0]
  
  # PLoS doc IDs should look like '10.1371.journal.pone.0015617.Abstract.2'
  # Convert to DOI like '10.1371/journal.pone.0015617'
  # Then convert DOI to PMID.
  if doi_to_pmid:
    plos_toks = doc_id.split('.')
    if plos_toks[2] == 'journal' and plos_toks[3].startswith("p"):
      doi_id = '.'.join(plos_toks[:2]) + '/' + '.'.join(plos_toks[2:5])
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


def gene_symbol_to_ensembl_id_map():
  """Maps a gene symbol from CHARITE -> ensembl ID"""
  with open('%s/onto/data/ensembl_genes.tsv' % util.APP_HOME) as f:
    eid_map = defaultdict(set)
    for line in f:
      eid, phrase, mapping_type = line.rstrip('\n').split('\t')
      eid_map[phrase].add(eid)
      eid_map[phrase.lower()].add(eid)
  return eid_map


def read_manual_list(name):
  """Reads in simple list of words in TSV format"""
  words = []
  with open('%s/onto/manual/%s.tsv' % (util.APP_HOME, name)) as f:
    for line in f:
      words.append(line.strip().lower())
  return frozenset(words)
