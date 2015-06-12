#!/usr/bin/env python
import sys

sys.path.append('../code')
import extractor_util as util
import data_util as dutil

if __name__ == '__main__':
  uniprot_to_hgnc = dict()
  with open('%s/onto/data/hgnc_to_uniprot.tsv' % util.APP_HOME) as f:
    for line in f:
      toks = line.strip(' \r\n').split('\t')
      if len(toks) == 2:
        hgnc = toks[0]
        uniprot = toks[1]
        uniprot_to_hgnc[uniprot] = hgnc

  num_unrecognized = 0
  with open('%s/onto/data/reactome_uniprot.tsv' % util.APP_HOME) as f:
    for line in f:
      toks = line.strip(' \r\n').split('\t')
      uniprot = toks[0].split('-')[0]  # Ignore isoform number = thing after hyphen
      pathway_id = toks[1]
      name = toks[2]
      if uniprot in uniprot_to_hgnc:
        hgnc = uniprot_to_hgnc[uniprot]
        util.print_tsv_output((pathway_id, hgnc, name))
      else:
        num_unrecognized += 1
        # print >> sys.stderr, 'Unrecognized Uniprot ID %s' % uniprot
  print >> sys.stderr, 'Found %d unrecognized Uniprot IDs in Reactome' % (
      num_unrecognized)
