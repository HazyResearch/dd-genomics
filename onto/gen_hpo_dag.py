#!/usr/bin/env python
import sys
sys.path.append('../code')

import extractor_util as util
import data_util as dutil

if __name__ == '__main__':
  hpo_dag = dutil.read_hpo_dag()
  if len(sys.argv) > 1:
    hpo_phenos = set(dutil.get_hpo_phenos(hpo_dag, parent=sys.argv[1]))
  else:
    hpo_phenos = set(dutil.get_hpo_phenos(hpo_dag))
  print >> sys.stderr, 'Found %d HPO phenotypes of %d terms' % (
      len(hpo_phenos), len(hpo_dag.nodes))
  for child in hpo_dag.nodes:
    for parent in hpo_dag.edges[child]:
      util.print_tsv_output((parent, child, child in hpo_phenos))
