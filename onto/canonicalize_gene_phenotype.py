#! /usr/bin/env python

import sys
sys.path.append('../code')
import data_util as dutil
import os

APP_HOME = os.environ['GDD_HOME']

def get_parents(bottom_id, hpo_dag, parent='HP:0000118'):
  """Get only the children of 'Phenotypic Abnormality' (HP:0000118)."""
  rv = [hpo_term for hpo_term in hpo_dag.nodes if hpo_dag.has_child(parent, hpo_term) and hpo_dag.has_child(hpo_term, bottom_id)]
  if bottom_id not in rv:
    rv.append(bottom_id)
  if not 'HP:0000118' in rv:
    rv = []
  return rv

if __name__ == '__main__':
  hpo_dag = dutil.read_hpo_dag()
  with open('%s/onto/raw/phenotype_to_gene.map' % APP_HOME) as f:
    for line in f:
      toks = line.strip().split()
      hpo_id = toks[0]
      ensemble_gene = toks[1]
      parent_ids = get_parents(hpo_id, hpo_dag) # includes the original hpo_id
      for parent_id in parent_ids:
        sys.stdout.write('{0}\t{1}\n'.format(parent_id, ensemble_gene))
      sys.stdout.flush()
