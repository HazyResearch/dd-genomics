import sys
import re

disease_to_hpos = {}
with open('data/hpo_disease_phenotypes.tsv', 'rb') as f:
  for line in f.readlines():
    source, source_id, name, name2, hpos = line.strip().split('\t')
    if source == "OMIM":
      disease_to_hpos[source_id] = hpos.split("|")

with open('raw/clinvar.tsv', 'rb') as f:
  for line in f.readlines():
    row = line.strip().split('\t')
    pheno_ids = row[10]
    try:
      hgvs = [n.split(':')[1] for n in (row[18], row[19]) if len(n.strip()) > 0]
    except IndexError:
      #sys.stderr.write('\t'.join([row[18], row[19]])+'\n')
      pass
    omim_match = re.search(r'OMIM:(\d+),', pheno_ids)
    if omim_match:
      omim_id = omim_match.group(1)
      hpos = disease_to_hpos.get(omim_id)
      if hpos:
        for variant in hgvs:
          for pheno in hpos:
            print '%s\t%s' % (variant, pheno)
