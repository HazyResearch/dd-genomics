#! /usr/bin/env python

import sys
sys.path.append('../code')
import data_util as dutil
import os

APP_HOME = os.environ['GDD_HOME']

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
  with open('%s/onto/manual/harendra_phenotype_to_gene.map' % APP_HOME) as f:
    for line in f:
      toks = line.strip().split()
      hpo_id = toks[0]
      ensemble_gene = toks[1]
      parent_ids = get_parents(hpo_id, hpo_dag) # includes the original hpo_id

      assert hpo_id in parent_ids
      if 'HP:0000118' not in parent_ids:
      # sys.stderr.write('line "{0}": not a phenotypic abnormality\n'.format(line.strip()))
        continue
      parent_ids.remove('HP:0000118')
      for parent_id in parent_ids:
        sys.stdout.write('{0}\t{1}\n'.format(parent_id, ensemble_gene))
      sys.stdout.flush()