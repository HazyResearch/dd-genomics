#! /usr/bin/env python

import os
APP_HOME = os.environ['GDD_HOME']
import sys
sys.path.append('%s/code' % APP_HOME)
import data_util as dutil


### ATTENTION!!!! PLEASE PIPE THE OUTPUT OF THIS SCRIPT THROUGH sort | uniq !!! ###
### Doing it within python is a waste of resources. Linux does it much faster.  ###

def get_parents(bottom_id, dag, root_id='HP:0000118'):
    if bottom_id == root_id:
      return set([bottom_id])
    rv = set()
    if bottom_id in dag.edges:
      for parent in dag.edges[bottom_id]:
        rv |= get_parents(parent, dag)
    rv.add(bottom_id)
    return rv

if __name__ == '__main__':
  hpo_dag = dutil.read_hpo_dag()
  with open('%s/onto/data/hpo_phenotypes.tsv' % APP_HOME) as f:
    for line in f:
      toks = line.strip().split('\t')
      hpo_id = toks[0]
      pheno_name = toks[1]
      parent_ids = get_parents(hpo_id, hpo_dag) # includes the original hpo_id

      assert hpo_id in parent_ids
      if 'HP:0000118' not in parent_ids:
        continue
      sys.stdout.write(hpo_id + '\t' + pheno_name + '\n')
      sys.stdout.flush()
