#! /usr/bin/env python

import os
APP_HOME = os.environ['GDD_HOME']
import sys
sys.path.append('%s/code' % APP_HOME)
import data_util as dutil
import argparse

### ATTENTION!!!! PLEASE PIPE THE OUTPUT OF THIS SCRIPT THROUGH sort | uniq !!! ###
### Doing it within python is a waste of resources. Linux does it much faster.  ###

if __name__ == '__main__':
  hpo_dag = dutil.read_hpo_dag()
  parser = argparse.ArgumentParser()
  parser.add_argument('--only-abnormalities', required=False, action="store_true")
  args = parser.parse_args()
  for line in sys.stdin:
    toks = line.strip().split()
    hpo_id = toks[0]
    ensemble_gene = toks[1]
    parent_ids = dutil.get_parents(hpo_id, hpo_dag) # includes the original hpo_id

    assert hpo_id in parent_ids
    if args.only_abnormalities:
      if 'HP:0000118' not in parent_ids:
        sys.stderr.write('"{0}": not a phenotypic abnormality\n'.format(hpo_id.strip()))
        continue
      parent_ids.remove('HP:0000118')
    for parent_id in parent_ids:
      sys.stdout.write('{0}\t{1}\n'.format(parent_id, ensemble_gene))
    sys.stdout.flush()
