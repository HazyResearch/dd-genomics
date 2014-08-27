#! /usr/bin/env python3

import fileinput
import json
import random

from dstruct.Sentence import Sentence
from dstruct.Relation import Relation

SUPERVISION_PROB = 0.5
SUPERVISION_GENEHPOTERM_DICT_FRACTION = 0.4

## Perform distant supervision
def supervise(relation, gene_mention, hpoterm_mention, sentence):
    if random.random() < SUPERVISION_PROB and relation.bla in supervision_genehpoterm_dict:
        relation.is_correct = True


## Add features
def add_features(relation, gene_mention, hpoterm_mention, sentence):
    # Add features
    gene_start = int(gene_mention.id.split("_")[4])
    hpoterm_start = int(hpoterm_mention.id.split("_")[4])
    gene_end = int(gene_mention.id.split("_")[5])
    hpoterm_end = int(hpoterm_mention.id.split("_")[5])
    start = min(gene_start, hpoterm_start)
    end = max(gene_end, hpoterm_end)
    # Present in the existing HPO mapping
    relation.add_feature("IN_GENE_HPOTERM_MAP={}".format(int(frozenset([gene_mention.symbol,
        hpoterm_mention.term.lower()]) in genehpoterm_dict)))
    # Verb between the two words, if present
    # XXX (Matteo) From pharm, RelationExtractor_Druggene_mention.py, but not correct
    #for word in sentence.words[start:end]: 
    #    if re.search('^VB[A-Z]*$', word.pos):
    #        relation.add_feature("verb="+word.lemma])
    # Word sequence between words
    relation.add_feature("word_seq="+"_".join([w.lemma for w in sentence.words[start:end]]))
    # Left and right windows
    if start > 0:
        relation.add_feature("WINDOW_LEFT_1={}".format(sentence.words[start-1]))
    if end < len(sentence.words) - 1:
        relation.add_feature("WINDOW_RIGHT_1={}".format(sentence.words[end]))
    # Shortest dependency path between the two mentions
    relation.add_feature(sentence.dep_path(gene_mention, hpoterm_mention))


## Yield the relations (actually only one per call, but we follow the
## behavior of extract() in other extractors)
def extract(gene_mention, hpoterm_mention, sentence):
    relation = Relation("GENEHPOTERM", gene_mention, hpoterm_mention)
    add_features(relation, gene_mention, hpoterm_mention, sentence)
    yield relation


# Process input
with fileinput.input as input_files:
    for line in input_files:
        row = json.loads(line)
        gene_mention = deserialize(row["gene"])
        hpoterm_mention = deserialize(row["hpoterm"])

        sentence = Sentence(row["doc_id"], row["sent_id"], row["wordidxs"],
                row["words"], row["poses"], row["ners"], row["lemmas"],
                row["dep_paths"], row["dep_parents"], row["bounding_boxes"])
        for relation in extract(gene_mention, hpoterm_mention, sentence):
            supervise(relation, gene_mention, hpoterm_mention, sentence)


