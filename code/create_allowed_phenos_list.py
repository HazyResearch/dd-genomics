#! /usr/bin/env python

from data_util import get_hpo_phenos, get_parents, read_hpo_dag

if __name__ == "__main__":
  hpo_dag = read_hpo_dag()
  allowed_phenos = set(get_hpo_phenos(hpo_dag))
  for hpo_id in allowed_phenos:
    parent_ids = get_parents(hpo_id, hpo_dag) # includes the original hpo_id
    assert hpo_id in parent_ids
    if 'HP:0000118' not in parent_ids:
      sys.stderr.write('line "{0}": not a phenotypic abnormality\n'.format(line.strip()))
      continue
    parent_ids.remove('HP:0000118')
    for parent_id in parent_ids:
      allowed_phenos.add(parent_id)
  for hpo_id in allowed_phenos:
    print hpo_id
