#! /usr/bin/env python3

import fileinput
import json
import random

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation

from helper.dictionaries import load_dict

SUPERVISION_PROB = 0.5
SUPERVISION_GENEHPOTERMS_DICT_FRACTION = 0.4

## Perform distant supervision
def supervise(relation, gene_mention, hpoterm_mention, sentence):
    if random.random() < SUPERVISION_PROB and relation.bla in supervision_genehpoterms_dict:
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
        hpoterm_mention.term.lower()]) in genehpoterms_dict)))
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


# Load the gene<->hpoterm dictionary
genehpoterms_dict = load_dict("genehpoterms")
# Create supervision dictionary that only contains a fraction of the genes in the gene
# dictionary. This is to avoid that we label as positive examples everything
# that is in the dictionary
supervision_genehpoterms_dict = dict()
to_sample = set(random.sample(range(len(genehpoterms_dict)),
        int(len(genehpoterms_dict) * SUPERVISION_GENEHPOTERMS_DICT_FRACTION)))
i = 0
for hpoterm in genehpoterms_dict:
    if i in to_sample:
        supervision_genehpoterms_dict[hpoterm] = genehpoterms_dict[hpoterm]
    i += 1

if __name__ == "__main__":
    # Process input
    with fileinput.input as input_files:
        for line in input_files:
            row = json.loads(line)
            # Create the sentence object where the two mentions appear
            sentence = Sentence(row["doc_id"], row["sent_id"], row["wordidxs"],
                    row["words"], row["poses"], row["ners"], row["lemmas"],
                    row["dep_paths"], row["dep_parents"], row["bounding_boxes"])
            # Create the mentions
            gene_mention = Mention("GENE", row["gene_entity"],
                    [sentence.words[i] for i in row["gene_wordidxs"]])
            hpoterm_mention = Mention("HPOTERM", row["hpoterm_entity"],
                    [sentence.words[i] for i in row["hpoterm_wordidxs"]])
            # Create the relation
            relation = Relation("GENEHPOTERM", gene_mention, hpoterm_mention)
            # Add features
            add_features(relation, gene_mention, hpoterm_mention, sentence)
            # Supervise
            supervise(relation, gene_mention, hpoterm_mention, sentence)
            # Print!
            print(relation.json_dump())

