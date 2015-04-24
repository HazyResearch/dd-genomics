#!/usr/bin/env python
import collections
import random
import sys

import extractor_util as util

def read_gene_pheno_hpo():
  """Get gene -> phenotype associations from HPO."""
  gene_pheno = collections.defaultdict(set)
  with open('%s/onto/data/hpo_phenotype_genes.tsv' % util.APP_HOME) as f:
    for line in f:
      pheno, gene = line.strip().split('\t')
      gene_pheno[gene].add(pheno)
  return gene_pheno


def main():
  frac_negative = float(sys.argv[1])
  hpo_dag = util.read_hpo_dag()
  if len(sys.argv) > 2:
    hpo_phenos = set(util.get_hpo_phenos(hpo_dag, parent=sys.argv[2]))
  else:
    hpo_phenos = set(util.get_hpo_phenos(hpo_dag))
  print >> sys.stderr, 'Found %d HPO phenotypes of %d terms' % (
      len(hpo_phenos), len(hpo_dag.nodes))

  gene_pheno = read_gene_pheno_hpo()
  print >> sys.stderr, 'Generating all candidates.'
  num_positive = 0
  num_negative = 0
  for gene in gene_pheno:
    if len(hpo_phenos & gene_pheno[gene]) == 0: continue  # Skip unannotated genes
    for pheno in hpo_phenos:
      if pheno in gene_pheno[gene]:
        is_correct = True
        num_positive += 1
      else:
        if random.random() <= frac_negative:
          is_correct = False
          num_negative += 1
        else:
          is_correct = None
      # insert a None for the id column.
      util.print_tsv_output((None, gene, pheno, is_correct))
  print >> sys.stderr, 'Generated %d positive, %d negative examples' % (
      num_positive, num_negative)


if __name__ == '__main__':
  if len(sys.argv) <= 1:
    print >> sys.stderr, 'Usage: %s FRAC_NEGATIVE_EXAMPLES [HP:???]' % sys.argv[0]
    sys.exit(1)
  main()
