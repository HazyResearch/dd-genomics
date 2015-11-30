#! /usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
from nltk.stem import WordNetLemmatizer
import re
from nltk.corpus import stopwords

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

def comp_gene_rgxs(ensembl_genes_path):
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

def replace_genes(content, genes_rgx):
  return genes_rgx.sub(' ENSEMBLGENE ', content)

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

lemmatizer = WordNetLemmatizer()
def lemmatize(content):
  return [lemmatizer.lemmatize(s) for s in content]

no_alnum = re.compile(r'[\W_ ]+')
if __name__ == "__main__":
  if len(sys.argv) != 4:
    print >>sys.stderr, "need 3 args: symbol for file (NOT used for stdin), ensembl genes path, output path"
    sys.exit(1)
  pubmed = sys.argv[1]
  ensembl_genes_path = sys.argv[2]
  out_path = sys.argv[3]
  gene_rgx = comp_gene_rgxs(ensembl_genes_path)
  with open(out_path, 'w') as f:
    ctr = -1
    for line in sys.stdin:
      ctr += 1
      if ctr % 500 == 0:
        print >>sys.stderr, "replacing %d lines in %s " % (ctr, pubmed)
      item = json.loads(line)
      pmid = item['doc-id']
      content = item['content']
      content = replace_genes(content, gene_rgx)
      content = replace_variants(content)
      content = [w for w in no_alnum.sub(' ', content).lower().split() if w not in stopwords.words('english')]
      # content = no_alnum.sub(' ', content).lower()
      print >>f, "%s\t%s" % (pmid, ' '.join(lemmatize(content)))
