#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib

Row = namedtuple('Row', ['relation_id', 'doc_id', 'sent_id', 'gene_mention_id', 'gene_wordidxs',
            'pheno_mention_id', 'pheno_wordidxs', 'words', 'lemmas', 'poses', 'ners', 'dep_paths',
            'dep_parents', 'wordidxs'])

def parse_input_row(line):
  tokens = line.split('\t')
  return Row(relation_id=tokens[0],
             doc_id=tokens[1],
             sent_id=int(tokens[2]),
             gene_mention_id=tokens[3],
             gene_wordidxs=util.tsv_string_to_list(tokens[4], func=int),
             pheno_mention_id=tokens[5],
             pheno_wordidxs=util.tsv_string_to_list(tokens[6], func=int),
             words=util.tsv_string_to_list(tokens[7]),
             lemmas=util.tsv_string_to_list(tokens[8]),
             poses=util.tsv_string_to_list(tokens[9]),
             ners=util.tsv_string_to_list(tokens[10]),
             dep_paths=util.tsv_string_to_list(tokens[11]),
             dep_parents=util.tsv_string_to_list(tokens[12], func=int),
             wordidxs=util.tsv_string_to_list(tokens[13], func=int))

def create_ddlib_sentence(row):
  """Create a list of ddlib.Word objects from input row."""
  dds = []
  for i, word in enumerate(row.words):
    dds.append(ddlib.Word(
        begin_char_offset=None,
        end_char_offset=None,
        word=word,
        lemma=row.lemmas[i],
        pos=row.poses[i],
        ner=row.ners[i],
        dep_par=row.dep_parents[i],
        dep_label=row.dep_paths[i]))
  return dds

def get_features_for_candidate(row):
  """Extract features for candidate mention- both generic ones from ddlib & custom features"""
  features = []
  dds = create_ddlib_sentence(row)

  # (1) GENERIC FEATURES from ddlib
  gene_span = ddlib.Span(begin_word_id=row.gene_wordidxs[0], length=len(row.gene_wordidxs))
  pheno_span = ddlib.Span(begin_word_id=row.pheno_wordidxs[0], length=len(row.pheno_wordidxs))
  features += [(row.doc_id, row.relation_id, feat) \
                    for feat in ddlib.get_generic_features_relation(dds, gene_span, pheno_span)]
  return features

# Helper for loading in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)

def main():

  # Load user-defined dictionaries to be used in ddlib
  ddlib.load_dictionary(onto_path("manual/genepheno_keywords.txt"), dict_id="gp_relation_kws")

  # Extract features from each line
  features = []
  for line in sys.stdin:
    row = parse_input_row(line)
    try:
      features += get_features_for_candidate(row)
    except Exception as e:
      util.print_error("ERROR in row.relation_id=%s" % (row.relation_id,))
      util.print_error(e)

  for feature in features:
    util.print_tsv_output(feature)

if __name__ == '__main__':
  main()
