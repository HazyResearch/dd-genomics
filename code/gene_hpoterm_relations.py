#! /usr/bin/env python3

import fileinput
import re

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2list


# Add features
def add_features(relation, gene_mention, hpoterm_mention, sentence):
    # Add features
    gene_start = gene_mention.wordidxs[0]
    hpoterm_start = hpoterm_mention.wordidxs[0]
    gene_end = gene_mention.wordidxs[-1]
    hpoterm_end = hpoterm_mention.wordidxs[-1]
    limits = sorted((gene_start, hpoterm_start, gene_end, hpoterm_end))
    start = limits[0]
    betw_start = limits[1]
    betw_end = limits[2]
    end = limits[3]

    # Verb between the two words, if present
    for word in sentence.words[betw_start+1:betw_end]:
        if re.search('^VB[A-Z]*$', word.pos) and word.lemma != ")" and \
                word.lemma != "(":
            relation.add_feature("VERB_" + word.lemma)
    # Shortest dependency path between the two mentions
    relation.add_feature("DEP_PATH_[" + sentence.dep_path(gene_mention,
        hpoterm_mention) + "]")
    # The sequence of lemmas between the two mentions
    seq = "_".join(map(lambda x: x.lemma,
                       sentence.words[betw_start+1:betw_end]))
    relation.add_feature("WORD_SEQ_[" + seq + "]")
    # The sequence of words between the two mentions but using the NERs, if
    # present
    seq_list = []
    for word in sentence.words[betw_start+1:betw_end]:
        if word.ner != "O":
            seq_list.append(word.ner)
        else:
            seq_list.append(word.lemma)
    seq = "_".join(seq_list)
    relation.add_feature("WORD_SEQ_NER_[" + seq + "]")
    # Lemma on the left and on the right
    if start > 0:
        relation.add_feature("NGRAM_LEFT_1_[" + sentence.words[start-1].lemma +
                             "]")
    if end < len(sentence.words) - 1:
        relation.add_feature("NGRAM_RIGHT_1_[" + sentence.words[end+1].lemma +
                             "]")


# Load the gene<->hpoterm dictionary
genehpoterms_dict = load_dict("genehpoterms")

if __name__ == "__main__":
    # Process input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
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
            # If the word indexes do not overlap, create the relation candidate
            if not set(line_dict["gene_wordidxs"]) & \
                    set(line_dict["hpoterm_wordidxs"]):
                relation = Relation(
                    "GENEHPOTERM", gene_mention, hpoterm_mention)
            # Add features
            add_features(relation, gene_mention, hpoterm_mention, sentence)
            # Supervise
            # One of the two mentions is labelled as False
            if gene_mention.is_correct is False or \
                    hpoterm_mention.is_correct is False:
                supervised = Relation(
                    "GENEHPOTERM_SUP", gene_mention, hpoterm_mention)
                supervised.features = relation.features
                supervised.is_correct = False
                print(supervised.tsv_dump())
            # Present in the existing HPO mapping
            in_mapping = False
            hpo_entity_id = hpoterm_mention.entity.split("|")[0]
            for gene in gene_mention.entity.split("|"):
                if frozenset([gene, hpo_entity_id]) in genehpoterms_dict:
                    in_mapping = True
            if frozenset([gene_mention.words[0].word, hpo_entity_id]) in \
                    genehpoterms_dict:
                in_mapping = True
            if in_mapping:
                supervised = Relation(
                    "GENEHPOTERM_SUP", gene_mention, hpoterm_mention)
                supervised.features = relation.features
                supervised.is_correct = True
                print(supervised.tsv_dump())
            # Print!
            print(relation.tsv_dump())
