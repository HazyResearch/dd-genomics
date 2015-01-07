#! /usr/bin/env python3

import fileinput
import re

from dstruct.Sentence import Sentence
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op, \
    print_feature

max_mention_length = 8  # This is somewhat arbitrary

NEG_PROB = 0.005  # Probability of generating a random negative mention


# Add features
def add_features(mention_id, mention_words, sentence):
    mention_wordidxs = []
    for word in mention_words:
        mention_wordidxs.append(word.in_sent_idx)
    # The first alphanumeric lemma on the left of the mention, if present,
    idx = mention_words[0].in_sent_idx - 1
    left_lemma_idx = -1
    left_lemma = ""
    while idx >= 0 and not sentence.words[idx].word.isalnum():
        idx -= 1
    try:
        left_lemma = sentence.words[idx].lemma
        try:
            float(left_lemma)
            left_lemma = "_NUMBER"
        except ValueError:
            pass
        left_lemma_idx = idx
        print_feature(
            sentence.doc_id, mention_id, "NGRAM_LEFT_1_[{}]".format(
                left_lemma))
    except IndexError:
        pass
    # The first alphanumeric lemma on the right of the mention, if present,
    idx = mention_wordidxs[-1] + 1
    right_lemma_idx = -1
    right_lemma = ""
    while idx < len(sentence.words) and not sentence.words[idx].word.isalnum():
        idx += 1
    try:
        right_lemma = sentence.words[idx].lemma
        try:
            float(right_lemma)
            right_lemma = "_NUMBER"
        except ValueError:
            pass
        right_lemma_idx = idx
        print_feature(
            sentence.doc_id, mention_id, "NGRAM_RIGHT_1_[{}]".format(
                right_lemma))
    except IndexError:
        pass
    # The lemma "two on the left" of the mention, if present
    try:
        print_feature(sentence.doc_id, mention_id, "NGRAM_LEFT_2_[{}]".format(
            sentence.words[left_lemma_idx - 1].lemma))
        print_feature(
            sentence.doc_id, mention_id, "NGRAM_LEFT_2_C_[{} {}]".format(
                sentence.words[left_lemma_idx - 1].lemma, left_lemma))
    except IndexError:
        pass
    # The lemma "two on the right" on the left of the mention, if present
    try:
        print_feature(
            sentence.doc_id, mention_id, "NGRAM_RIGHT_2_[{}]".format(
                sentence.words[right_lemma_idx + 1].lemma))
        print_feature(
            sentence.doc_id, mention_id, "NGRAM_RIGHT_2_C_[{} {}]".format(
                right_lemma, sentence.words[right_lemma_idx + 1].lemma))
    except IndexError:
        pass
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word in mention_words:
        for word2 in sentence.words:
            if word2.lemma in KEYWORDS:
                (p, l) = sentence.get_word_dep_path(
                    word.in_sent_idx, word2.in_sent_idx)
                kw = word2.lemma
                if word2.lemma in PATIENT_KWS:
                    kw = "_HUMAN"
                print_feature(
                    sentence.doc_id, mention_id, "KEYWORD_[" + kw + "]" + p)
                if l < minl:
                    minl = l
                    minp = p
                    minw = kw
    # Special feature for the keyword on the shortest dependency path
    if minw:
        print_feature(
            sentence.doc_id, mention_id,
            'EXT_KEYWORD_MIN_[' + minw + ']' + minp)
        print_feature(
            sentence.doc_id, mention_id, 'KEYWORD_MIN_[' + minw + ']')
    # The verb closest to the candidate
    minl = 100
    minp = None
    minw = None
    for word in mention_words:
        for word2 in sentence.words:
            if word2.word.isalpha() and re.search('^VB[A-Z]*$', word2.pos) \
                    and word2.lemma != 'be':
                (p, l) = sentence.get_word_dep_path(
                    word.in_sent_idx, word2.in_sent_idx)
                if l < minl:
                    minl = l
                    minp = p
                    minw = word2.lemma
        if minw:
            print_feature(
                sentence.doc_id, mention_id, 'VERB_[' + minw + ']' + minp)


# Keyword that seems to appear with phenotypes
VAR_KWS = frozenset([
    "abnormality", "affect", "apoptosis", "association", "cancer", "carcinoma",
    "case", "cell", "chemotherapy", "clinic", "clinical", "chromosome",
    "cronic", "deletion", "detection", "diagnose", "diagnosis", "disease",
    "drug", "family", "gene", "genome", "genomic", "genotype", "give", "grade",
    "group", "history", "infection", "inflammatory", "injury", "mutation",
    "pathway", "phenotype", "polymorphism", "prevalence", "protein", "risk",
    "severe", "stage", "symptom", "syndrome", "therapy", "therapeutic",
    "treat", "treatment", "variant" "viruses", "virus"])

PATIENT_KWS = frozenset(
    ["boy", "girl", "man", "woman", "men", "women", "patient", "patients"])

KEYWORDS = VAR_KWS | PATIENT_KWS

if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "mention_id", "mention_wordidxs"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    no_op, lambda x: TSVstring2list(x, int)])
            # Create the sentence object
            null_list = [None, ] * len(line_dict["wordidxs"])
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], null_list)
            if sentence.is_weird():
                continue
            mention_words = []
            for mention_wordidx in line_dict["mention_wordidxs"]:
                mention_words.append(sentence.words[mention_wordidx])
            add_features(line_dict["mention_id"], mention_words, sentence)
