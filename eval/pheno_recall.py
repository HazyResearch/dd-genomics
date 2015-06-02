"""Assess phenotype recall relative to known HPO-PMID map."""
import collections
import random
import sys

sys.path.append('../code')
import extractor_util as util
import data_util as dutil

NUM_ERRORS_TO_SAMPLE = 50

def main(id_file, candidate_file):
  # Load list of all pubmed IDs in the dataset
  print >> sys.stderr, 'Loading list of pubmed IDs from doc ID list.'
  doi_to_pmid = dutil.read_doi_to_pmid()
  pmids_in_data = set()
  num_docs = 0
  with open(id_file) as f:
    for line in f:
      doc_id = line.strip()
      pmid = dutil.get_pubmed_id_for_doc(doc_id, doi_to_pmid=doi_to_pmid)
      if pmid:
        pmids_in_data.add(pmid)
      num_docs += 1
  print >> sys.stderr, '%d/%d documents have PubMed IDs.' % (
      len(pmids_in_data), num_docs)

  # Load map from Pubmed ID to HPO term via MeSH
  print >> sys.stderr, 'Loading supervision data via MeSH'
  mesh_supervision = collections.defaultdict(set)
  with open('%s/onto/data/hpo_to_pmid_via_mesh.tsv' % util.APP_HOME) as f:
    for line in f:
      hpo_id, pmid = line.strip().split('\t')
      if pmid in pmids_in_data:
        mesh_supervision[pmid].add(hpo_id)

  # Identify all true pairs from MeSH
  true_pairs = set()
  for pmid in pmids_in_data:
    for hpo in mesh_supervision[pmid]:
      true_pairs.add((pmid, hpo))

  # Load map from Pubmed ID to HPO term based on extracted candidates
  print >> sys.stderr, 'Loading extracted pheno candidates'
  candidates = collections.defaultdict(set)
  with open(candidate_file) as f:
    for line in f:
      doc_id, hpo_id = line.strip().split('\t')
      pmid = dutil.get_pubmed_id_for_doc(doc_id, doi_to_pmid=doi_to_pmid)
      if pmid:
        candidates[pmid].add(hpo_id)

  # Load HPO DAG
  # We say we found a HPO term if we find either the exact HPO term
  # or one of its children
  hpo_dag = dutil.read_hpo_dag()

  # Determine which true pairs had candidate mentions for them
  found_pairs = set()
  missed_pairs = set()
  for pmid, hpo in true_pairs:
    found_hpo_ids = candidates[pmid]
    for cand_hpo in found_hpo_ids:
      if cand_hpo == '\N': continue
      if hpo_dag.has_child(hpo, cand_hpo):
        found_pairs.add((pmid, hpo))
        break
    else:
      missed_pairs.add((pmid, hpo))

  # Compute recall
  num_true = len(true_pairs)
  num_found = len(found_pairs)
  print >> sys.stderr, 'Recall: %d/%d = %g' % (
      num_found, num_true, float(num_found) / num_true)

  # Compute other statistics
  num_article = len(pmids_in_data)
  num_annotated = sum(1 for x in pmids_in_data if len(mesh_supervision[x]) > 0)
  print >> sys.stderr, '%d/%d = %g pubmed articles had HPO annotation' % (
      num_annotated, num_article, float(num_annotated) / num_article)

  # Read in HPO information
  hpo_info_dict = dict()
  with open('%s/onto/data/hpo_phenotypes.tsv' % util.APP_HOME) as f:
    for line in f:
      toks = line.strip('\r\n').split('\t')
      hpo_id = toks[0]
      hpo_info_dict[hpo_id] = toks[0:3]

  # Sample some error cases
  missed_sample = random.sample(list(missed_pairs), 100)
  for pmid, hpo in missed_sample:
    hpo_info = hpo_info_dict[hpo]
    pubmed_url = 'http://www.ncbi.nlm.nih.gov/pubmed/%s' % pmid
    hpo_url = 'www.human-phenotype-ontology.org/hpoweb/showterm?id=%s' % hpo
    toks = [pubmed_url, hpo_url] + hpo_info
    print '\t'.join(toks)


if __name__ == '__main__':
  if len(sys.argv) < 3:
    print >> sys.stderr, 'Usage: %s doc_ids.tsv candidates.tsv' % sys.argv[0]
    print >> sys.stderr, ''
    print >> sys.stderr, 'doc_ids.tsv should be list of doc ids'
    print >> sys.stderr, '  e.g. /lfs/raiders2/0/robinjia/data/genomics_sentences_input_data/50k_doc_ids.tsv'
    print >> sys.stderr, 'candidates.tsv should have rows doc_id, hpo_id.'
    print >> sys.stderr, '  e.g. result of SELECT doc_id, entity FROM pheno_mentions'
    print >> sys.stderr, '  or SELECT doc_id, entity FROM pheno_mentions_is_correct_inference WHERE expectation > 0.9'
    sys.exit(1)
  main(*sys.argv[1:])
