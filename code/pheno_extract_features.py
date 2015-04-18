#!/usr/bin/env python
import extractor_util as util
from collections import namedtuple
import os
import sys
import ddlib

# Load in manually defined keywords
onto_path = lambda p : '%s/onto/%s' % (os.environ['GDD_HOME'], p)
KWS = frozenset([w.strip() for w in open(onto_path('manual/pheno_sentence_keywords.tsv'), 'rb')])

Row = namedtuple('Row', ['doc_id', 'sent_id', 'words', 'lemmas', 'poses', 'ners',
            'dep_paths', 'dep_parents', 'mention_id', 'mention_wordidxs'])

def parse_input_row(line):
  tokens = line.split('\t')
  return Row(doc_id=tokens[0],
             sent_id=int(tokens[1]),
             words=util.tsv_string_to_list(tokens[2]),
             lemmas=util.tsv_string_to_list(tokens[3]),
             poses=util.tsv_string_to_list(tokens[4]),
             ners=util.tsv_string_to_list(tokens[5]),
             dep_paths=util.tsv_string_to_list(tokens[6]),
             dep_parents=util.tsv_string_to_list(tokens[7], func=int),
             mention_id=tokens[8],
             mention_wordidxs=util.tsv_string_to_list(tokens[9], func=int))

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
  span = ddlib.Span(begin_word_id=row.mention_wordidxs[0], length=len(row.mention_wordidxs))
  features += [(row.doc_id, row.mention_id, feat) \
                    for feat in ddlib.get_generic_features_mention(dds, span)]

  # (2) Add the closest verb by raw distance
  verb_idxs = [i for i,p in enumerate(row.poses) if p.startswith("VB")]
  if len(verb_idxs) > 0:
    dists = filter(lambda d : d[0] > 0, \
                   [(min([abs(i-j) for j in row.mention_wordidxs]), i) for i in verb_idxs])
    if len(dists) > 0:
      verb = row.lemmas[min(dists)[1]]
      features.append((row.doc_id, row.mention_id, 'NEAREST_VERB_[%s]' % (verb,)))

  # (3) Add the closest verb + its dep_path relation by dep_path distance
  # TODO: See if ddlib has dep path handling and/or build simple solution!
  # TODO: play around with more dep_path features in general!
  """
  verbs = []
  for mention_word_idx in row.mention_wordidxs:
    for word in dds.words:
      if word.word.isalpha() and re.search('^VB[A-Z]*$', word.pos):
        p, l = sentence.get_word_dep_path(mention_word_idx, word.in_sent_idx)
        verbs.append((l, p, word.lemma))
  if len(verbs) > 0:
    v = min(verbs)
    features.append((row.doc_id, row.mention_id, 'NEAREST_VERB_DEP_[%s_%s]' % (v[2], v[1])))
  """
  
  # (4) Add feature for any manually-defined keywords that appear in the sentence + dep paths
  # TODO: ddlib has a feature for this also leveraging dep_paths...
  for i,w in enumerate(row.lemmas):
    if i not in row.mention_wordidxs and w in KWS:
      features.append((row.doc_id, row.mention_id, 'KEYWORD_[%s]' % (w,)))
  return features

def main():
  features = []
  for line in sys.stdin:
    features += get_features_for_candidate(parse_input_row(line))
  for feature in features:
    util.print_tsv_output(feature)

if __name__ == '__main__':
  main()
