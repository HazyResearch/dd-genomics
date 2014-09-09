#! /usr/bin/env python3

import fileinput
import random
import re

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2list

SUPERVISION_PROB = 0.5
SUPERVISION_GENEHPOTERMS_DICT_FRACTION = 0.4
RANDOM_EXAMPLES_PROB = 0.01
RANDOM_EXAMPLES_QUOTA = 1000


# Perform distant supervision
def supervise(relation, gene_mention, hpoterm_mention, sentence):
    if random.random() < SUPERVISION_PROB:
        in_supervision_mapping = False
        for gene in gene_mention.entity.split("|"):
            if frozenset([gene, hpoterm_mention.entity]) in \
                    supervision_genehpoterms_dict:
                in_supervision_mapping = True
        if frozenset([gene_mention.words[0].word, hpoterm_mention.entity]) in \
                supervision_genehpoterms_dict:
            in_supervision_mapping = True
        if in_supervision_mapping:
            relation.is_correct = True


# Add features
def add_features(relation, gene_mention, hpoterm_mention, sentence):
    # Add features
    gene_start = gene_mention.wordidxs[0]
    hpoterm_start = hpoterm_mention.wordidxs[0]
    gene_end = gene_mention.wordidxs[-1]
    hpoterm_end = hpoterm_mention.wordidxs[-1]
    start = min(gene_start, hpoterm_start)
    end = max(gene_end, hpoterm_end)
    # Present in the existing HPO mapping
    in_mapping = False
    for gene in gene_mention.entity.split("|"):
        if frozenset([gene, hpoterm_mention.entity]) in genehpoterms_dict:
            relation.add_feature(
                "IN_GENE_HPOTERM_MAP_{}_{}".format(
                    gene, hpoterm_mention.entity))
            in_mapping = True
    if frozenset([gene_mention.words[0].word, hpoterm_mention.entity]) in \
            genehpoterms_dict:
        relation.add_feature(
            "IN_GENE_HPOTERM_MAP_{}_{}".format(
                gene_mention.words[0].word, hpoterm_mention.entity))
        in_mapping = True
    if in_mapping:
        relation.add_feature("IN_GENE_HPOTERM_MAP")
    # Verbs between the two words, if present
    # XXX (Matteo) From pharm, RelationExtractor_Druggene_mention.py, but not
    # correct (PERHAPS)
    for word in sentence.words[start:end]:
        if re.search('^VB[A-Z]*$', word.pos):
            relation.add_feature("VERB_"+word.lemma)
    # Word sequence between mentions
    relation.add_feature(
        "WORD_SEQ="+"_".join([w.lemma for w in sentence.words[start:end]]))
    # Left and right windows
    if start > 0:
        relation.add_feature(
            "WINDOW_LEFT_1={}".format(sentence.words[start-1].lemma))
    if end < len(sentence.words) - 1:
        relation.add_feature("WINDOW_RIGHT_1={}".format(
            sentence.words[end].lemma))
    # Shortest dependency path between the two mentions
    relation.add_feature(sentence.dep_path(gene_mention, hpoterm_mention))


# Load the gene<->hpoterm dictionary
genehpoterms_dict = load_dict("genehpoterms")
# Create supervision dictionary that only contains a fraction of the genes in
# the gene dictionary. This is to avoid that we label as positive examples
# everything that is in the dictionary
supervision_genehpoterms_dict = set()
to_sample = set(
    random.sample(
        range(len(genehpoterms_dict)),
        int(len(genehpoterms_dict) * SUPERVISION_GENEHPOTERMS_DICT_FRACTION)))
i = 0
for pair in genehpoterms_dict:
    if i in to_sample:
        supervision_genehpoterms_dict.add(pair)
    i += 1

if __name__ == "__main__":
    # Process input
    with fileinput.input() as input_files:
        for line in input_files:
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "bounding_boxes", "gene_entity", "gene_wordidxs",
                       "hpoterm_entity", "hpoterm_wordidxs"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list, no_op, lambda x: TSVstring2list(x, int),
                    no_op, lambda x: TSVstring2list(x, int)])
            # Create the sentence object where the two mentions appear
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Create the mentions
            gene_mention = Mention(
                "GENE", line_dict["gene_entity"],
                [sentence.words[j] for j in line_dict["gene_wordidxs"]])
            hpoterm_mention = Mention(
                "HPOTERM", line_dict["hpoterm_entity"],
                [sentence.words[j] for j in line_dict["hpoterm_wordidxs"]])
            # Create the relation
            relation = Relation("GENEHPOTERM", gene_mention, hpoterm_mention)
            # Add features
            add_features(relation, gene_mention, hpoterm_mention, sentence)
            # Supervise
            supervise(relation, gene_mention, hpoterm_mention, sentence)
            # Print!
            print(relation.tsv_dump())
