"""Assess phenotype recall relative to known HPO-PMID map."""
import collections
import sys

sys.path.append('../code')
import extractor_util as util

def main(id_file, candidate_file):
  # Load map from Pubmed ID to HPO term (via MeSH)
  print >> sys.stderr, 'Loading pubmed-to-HPO distant supervision data via MeSH'
  pmid_to_hpo = collections.defaultdict(set)
  with open('%s/onto/data/hpo_to_pmid_via_mesh.tsv' % util.APP_HOME) as f:
    for line in f:
      hpo_id, pmid = line.strip().split('\t')
      pmid_to_hpo[pmid].add(hpo_id)

  # Load list of all pubmed IDs in the dataset
  print >> sys.stderr, 'Loading list of pubmed IDs from doc ID list.'
  pmids_in_data = set()
  num_docs = 0
  with open(id_file) as f:
    for line in f:
      doc_id = line.strip()
      pmid = util.get_pubmed_id_for_doc(doc_id)
      if pmid:
        pmids_in_data.add(pmid)
      num_docs += 1
  print >> sys.stderr, '%d/%d documents have PubMed IDs.' % (
      len(pmids_in_data), num_docs)

  # Load doc_id + HPO candidate pairs
  print >> sys.stderr, 'Loading doc_id + HPO ID candidate pairs'
  good_pairs = set()
  for line in open(sys.argv[2]):
    doc_id, hpo_id = line.strip().split('\t')
    pmid = util.get_pubmed_id_for_doc(doc_id)
    if pmid and hpo_id in pmid_to_hpo[pmid]:
        good_pairs.add((pmid, hpo_id))

  # Compute oracle recall
  num_true = sum(len(pmid_to_hpo[x]) for x in pmids_in_data)
  num_found = len(good_pairs)
  print 'Oracle recall: %d/%d = %g' % (
      num_found, num_true, float(num_found) / num_true)

  # Compute other statistics
  num_article = len(pmids_in_data)
  num_annotated = sum(1 for x in pmids_in_data if len(pmid_to_hpo[x]) > 0)
  print '%d/%d = %g pubmed articles had HPO annotation' % (
      num_annotated, num_article, float(num_annotated) / num_article)


if __name__ == '__main__':
  if len(sys.argv) < 3:
    print >> sys.stderr, 'Usage: %s doc_ids.tsv candidates.tsv' % sys.argv[0]
    print >> sys.stderr, ''
    print >> sys.stderr, 'doc_ids.tsv should be list of doc ids'
    print >> sys.stderr, '  e.g. /lfs/raiders2/0/robinjia/data/genomics_sentences_input_data/50k_doc_ids.tsv'
    print >> sys.stderr, 'candidates.tsv should have rows doc_id, hpo_id.'
    print >> sys.stderr, '  e.g. result of SELECT doc_id, entity FROM pheno_mentions'
    sys.exit(1)
  main(*sys.argv[1:])
