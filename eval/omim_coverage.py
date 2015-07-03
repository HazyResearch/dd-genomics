import collections
import random
import sys

sys.path.append('../code')
import extractor_util as util
import data_util as dutil

HPO_DAG = dutil.read_hpo_dag()

def read_supervision():
  """Reads genepheno supervision data (from charite)."""
  supervision_pairs = set()
  with open('%s/onto/data/hpo_phenotype_genes.tsv' % util.APP_HOME) as f:
    for line in f:
      hpo_id, gene_symbol = line.strip().split('\t')

      # Canonicalize i.e. include all parents of hpo entities
      hpo_ids = [hpo_id] + [parent for parent in HPO_DAG.edges[hpo_id]]
      eids = EID_MAP[gene_symbol]
      for h in hpo_ids:
        for e in eids:
          supervision_pairs.add((h,e))
  return supervision_pairs

supervision_pairs = read_supervision()

# TODO: PIPE SQL IN HERE
"""
SELECT
  gene_entity
  pheno_entity
FROM
  genepheno_relations_is_correct_inference
WHERE
  expectation >= 0.9;
"""
extracted_pairs = []


# TODO to compare / visualize:
# (1) overall number new extracted e.g.
print len(set(extracted_pairs).difference(supervision_pairs))

# (2) difference in coverage on gene axis e.g. something with
set([p[0] for p in extracted_pairs]).difference([p[0] for p in supervision_pairs])

# (3) difference in coverage on pheno axis e.g. something with
set([p[1] for p in extracted_pairs]).difference([p[1] for p in supervision_pairs])
