#! /usr/bin/python
# -*- coding: utf-8 -*-

import word_counter
import sys
import re
from bunch import *
import numpy as np
import random
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from functools32 import lru_cache
from nltk.stem import PorterStemmer

def toBunch(mmap):
  rv = Bunch()
  rv.data = []
  rv.pmids = []
  rv.target = []
  for pmid in mmap:
    rv.data.append(mmap[pmid][1])
    rv.pmids.append(pmid)
    rv.target.append(mmap[pmid][0])
  rv.target = np.array(rv.target)
  return rv

def lemmatize_select(lemmatize, word):
  if word.startswith('MeSH_') or word == 'GENEVARIANT' or word == 'ENSEMBLGENE':
    return word
  return lemmatize(word)

sw = stopwords.words('english')

def lemmatize(bunch):
  print >>sys.stderr, "Lemmatizing data"
  new_data = []
  pattern = re.compile('[\W_]+]')
  # lemmatizer = WordNetLemmatizer()
  lemmatizer = PorterStemmer()
  # lemmatize = lru_cache(maxsize=5000)(lemmatizer.stem)
  # lemmatize = lemmatizer.stem
  lemmatize = lambda x : x.lower()
  ctr = -1
  for content in bunch.data:
    ctr += 1
    if ctr % 100 == 0:
      print >>sys.stderr, "lemmatizing %d lines" % ctr
    stripped = pattern.sub('', content.strip())
    split = stripped.split()
    new_content = ' '.join([lemmatize_select(lemmatize, s) for s in split if s not in sw])
    new_data.append(new_content)
  bunch.data = new_data
  return bunch

def make_mesh_terms(mesh):
  no_alnum = re.compile(r'[\W_]+')
  return ' '.join(['MeSH_' + no_alnum.sub('_', term) for term in mesh.split('|^|')])

def load_gene_name_to_genes(ensembl_genes_path):
  ret = {}
  with open(ensembl_genes_path) as f:
    for line in f:
      eid = line.strip().split(':')[0]
      canonical_name = (line.strip().split(':')[1]).split()[0]
      name = line.strip().split()[1]
      mapping_type = line.strip().split()[2]
      ret[name] = (eid, canonical_name, mapping_type)
  return ret 

min_word_len = {'ENSEMBL_ID': 2, 'REFSEQ': 2, 'NONCANONICAL_SYMBL': 4, 'CANONICAL_SYMBOL': 2}
bad_genes = ['ANOVA', 'MRI', 'CO2', 'gamma', 'spatial', 'tau', 'Men', 'ghrelin', 'MIM', 'NHS', 'STD', 'hole']

def comp_gene_rgx(ensembl_genes_path):
  print >>sys.stderr, "Computing gene regex"
  gene_names = []
  gene_name_to_genes = load_gene_name_to_genes(ensembl_genes_path)
  for name in gene_name_to_genes:
    if name in bad_genes:
      continue
    (eid, canonical_name, mapping_type) = gene_name_to_genes[name]
    if mapping_type not in ['CANONICAL_SYMBOL', 'NONCANONICAL_SYMBOL']:
      continue
    if mapping_type == 'NONCANONICAL_SYMBOL':
      min_len = 4 
    else:
      min_len = 2 
    if len(name) < min_len:
      continue
    if not re.match(r'.*[a-zA-Z].*', name):
      continue
    gene_names.append('[\.,_ \(\)]' + name + '[\.,_ \(\)]')
  return re.compile('(' + '|'.join(gene_names) + ')')

def replace_genes(content, gene_rgx):
  return gene_rgx.sub(' ENSEMBLGENE ', content)

a = r'[cgrnm]'
i = r'IVS'
b = r'ATCGatcgu'

s1 = r'0-9\_\.\:'
s2 = r'\/>\?\(\)\[\]\;\:\*\_\-\+0-9'
s3 = r'\/><\?\(\)\[\]\;\:\*\_\-\+0-9'

b1 = r'[%s]' % b 
bs1 = r'[%s%s]' % (b,s1)
bs2 = r'[%s %s]' % (b,s2)
bs3 = r'[%s %s]' % (b,s3)

c1 = r'(inv|del|ins|dup|tri|qua|con|delins|indel)'
c2 = r'(del|ins|dup|tri|qua|con|delins|indel)'
c3 = r'([Ii]nv|[Dd]el|[Ii]ns|[Dd]up|[Tt]ri|[Qq]ua|[Cc]on|[Dd]elins|[Ii]ndel|fsX|fsx|fs)'

p = r'CISQMNPKDTFAGHLRWVEYX'
ps2 = r'[%s %s]' % (p, s2)
ps3 = r'[%s %s]' % (p, s3)

d = '[ATCGRYUatgc]'

aa_long_to_short = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
  'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
  'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
  'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
aa_camel = {}
for aa in aa_long_to_short:
  aa_camel[aa[0] + aa[1].lower() + aa[2].lower()] = aa_long_to_short[aa]

aal = '(' + '|'.join([x for x in aa_long_to_short] + [x for x in aa_camel]) + ')'

# regexes from tmVar paper
# See Table 3 in http://bioinformatics.oxfordjournals.org/content/early/2013/04/04/bioinformatics.btt156.full.pdf
def comp_gv_rgxs():
  print >>sys.stderr, "Computing variants regex"
  GV_RGXS = [
  r'^([cgrnm]\.)?([0-9]+)([_]+([0-9]+))([\+\-\*][0-9]+)?(%s)[->/→](%s)' % (d, d),
  r'^([cgrnm]\.)?([0-9]+)([_]+([0-9]+))?([\+\-\*][0-9]+)?(%s)(%s+)?' % (c3, d),
  r'^[cgrnm]\.([0-9]+)?([\+\-\*][0-9]+)?(%s)[->/→](%s)' % (d, d),
  r'^[cgrnm]\.([0-9]+)?([\+\-\*][0-9]+)?(%s)' % d,
  r'^IVS([0-9]*[abcd]?)([\+\-\*][0-9]+)?(%s)-*[>/→](%s)' % (d, d),
  r'^IVS([0-9]*[abcd]?)([\+\-\*][0-9]+)?(%s?)(%s+)' % (c3, d),
  r'^p\.(([%s])|%s)([0-9]+)(([%s])|%s)' % (p, aal, p, aal),
  r'^p\.(([%s])|%s)([0-9]+)[_]+(([%s])|%s)([0-9]+)(%s)' % (p, aal, p, aal, c3),
  r'^p\.(([%s])|%s)([0-9]+)(%s)' % (p, aal, c3),
  r'^(%s)([0-9]+)(%s)' % (d, d)
  ]
  return re.compile('(' + '|'.join(GV_RGXS) + ')', flags=re.I)

gv_rgx = comp_gv_rgxs()

def replace_variants(content):
  return gv_rgx.sub(' GENEVARIANT ', content)

def load_unlabeled_docs(data_path, gene_rgx):
  no_alnum = re.compile(r'[\W_ ]+')
  rv = {}
  print >>sys.stderr, "Loading JSON data"
  ctr = -1
  with open(data_path) as f:
    for line in f:
      ctr += 1
      if ctr % 100 == 0:
        print >>sys.stderr, "counting %d lines" % ctr
      item = line.strip().split('\t')
      pmid = item[0]
      content = item[1]
      content.replace('\n', ' ')
      content = replace_genes(content, gene_rgx)
      content = replace_variants(content)
      content = no_alnum.sub(' ', content)
      if len(item) >= 8:
        mesh_terms = item[7]
      else:
        mesh_terms = ''

      if pmid in rv:
        rv[pmid] += ' ' + content
      else:
        rv[pmid] = content
        rv[pmid] += ' ' + make_mesh_terms(mesh_terms)
  b = Bunch()
  b.data = []
  b.pmids = []
  for pmid in rv:
    b.data.append(rv[pmid])
    b.pmids.append(pmid)
  return lemmatize(b)

if __name__ == "__main__":
  if len(sys.argv) != 4:
    print >>sys.stderr, "need 3 args: path to test pubmed TSV file to lemmatize etc, path to ensembl genes, output filename"
    sys.exit(1)
  testing_path = sys.argv[1]
  ensembl_genes_path = sys.argv[2]
  output_path = sys.argv[3]

  global gene_rgx
  gene_rgx = comp_gene_rgx(ensembl_genes_path)

  print >>sys.stderr, "Loading test set"
  test_docs = load_unlabeled_docs(testing_path, gene_rgx)
  with open(output_path, 'w') as f:
    for i, pmid in enumerate(test_docs.pmids):
      print >>f, "%s\t%s" % (pmid, test_docs.data[i])
