#! /usr/bin/env python3

import fileinput
import random
import re

from nltk.stem.snowball import SnowballStemmer

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.easierlife import get_all_phrases_in_sentence, \
    get_dict_from_TSVline, TSVstring2list, no_op
from helper.dictionaries import load_dict

max_mention_length = 8

NEG_PROB = 0.002

MENTION_THRESHOLD = 0.75

HPOTERM_KEYWORDS = frozenset([
    "abnormality", "affect", "apoptosis", "association", "boy", "cancer",
    "carcinoma", "case", "chemotherapy", "chromosome", "cronic", "deletion",
    "detection", "diagnose", "diagnosis", "disease", "drug", "gene", "genome",
    "genomic", "genotype", "girl", "give", "injury", "man", "mutation",
    "pathway", "patient", "patients", "phenotype", "polymorphism", "protein",
    "severe", "symptom", "syndrome", "therapy", "therapeutic", "treat",
    "treatment", "viruses", "virus", "woman"
    ])

# Load the dictionaries that we need
english_dict = load_dict("english")
stopwords_dict = load_dict("stopwords")
inverted_hpoterms = load_dict("hpoterms_inverted")
hponames_to_ids = load_dict("hponames_to_ids")
# hpodag = load_dict("hpoparents")

mandatory_stems = frozenset(
    ("keratocytosi", "carcinoma", "pancreat", "oropharyng", "hyperkeratos",
        "hyperkeratosi", "palmoplantar", "palmar", "genitalia", "labia",
        "hyperplasia", "fontanell", "facial", "prelingu", "sensorineur",
        "auditori", "neck", "incisor", "nervous", "ventricl", "cyst",
        "aplasia", "hypoplasia", "c-reactiv", "papillari",
        "beta-glucocerebrosidas", "loss", "accumul", "swell", "left", "right"))

stems = set()
mandatory = dict()
for hpo_name in inverted_hpoterms:
    stem_set = inverted_hpoterms[hpo_name]
    mandatory[stem_set] = stem_set & mandatory_stems
    stems |= stem_set
stems = frozenset(stems)

# The keys of the following dictionary are sets of stems, and the values are
# sets of hpoterms whose name, without stopwords, gives origin to the
# corresponding set of stems (as key)
hpoterms_dict = load_dict("hpoterms")

# Initialize the stemmer
stemmer = SnowballStemmer("english")


# Perform the supervision
def supervise(mentions, sentence):
    new_mentions = []
    for mention in mentions:
        new_mentions.append(mention)
        if mention.is_correct is not None:
            continue
        mention_lemmas = set([x.lemma.casefold() for x in mention.words])
        name_words = set([x.casefold() for x in
                          mention.entity.split("|")[1].split()])
        # The mention is exactly the hpo name
        if mention_lemmas == name_words:
            supervised = Mention("HPOTERM_SUP", mention.entity, mention.words)
            supervised.features = mention.features
            supervised.is_correct = True
            new_mentions.append(supervised)
            continue
        if "IS_PNEUNOMIAE" in mention.features:
            supervised = Mention("HPOTERM_SUP", mention.entity, mention.words)
            supervised.features = mention.features
            supervised.is_correct = False
            new_mentions.append(supervised)
            continue
    return new_mentions


# Add features
def add_features(mention, sentence):
    # The lemma on the left of the mention, if present, provided it's
    # alphanumeric but not a number or a stopword
    idx = mention.wordidxs[0] - 1
    while idx >= 0 and  \
            ((not sentence.words[idx].word.isupper() and
                sentence.words[idx].lemma in stopwords_dict) and
                not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word)
                or len(sentence.words[idx].lemma) == 1):
        idx -= 1
    if idx >= 0:
        mention.left_lemma = sentence.words[idx].lemma
        mention.add_feature("NGRAM_LEFT_1_[{}]".format(
            mention.left_lemma))
    # The word on the right of the mention, if present, provided it's
    # alphanumeric but not a number
    idx = mention.wordidxs[-1] + 1
    while idx < len(sentence.words) and \
            ((not sentence.words[idx].word.isupper() and
                sentence.words[idx].lemma in stopwords_dict) and
                not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word)
                or len(sentence.words[idx].lemma) == 1):
        idx += 1
    if idx < len(sentence.words):
        mention.right_lemma = sentence.words[idx].lemma
        mention.add_feature("NGRAM_RIGHT_1_[{}]".format(
            mention.right_lemma))
    # The word "two on the left" of the mention, if present
    if mention.wordidxs[0] > 1:
        mention.add_feature("NGRAM_LEFT_2_[{}]".format(
            sentence.words[mention.wordidxs[0] - 2].lemma))
    # The word "two on the right" on the left of the mention, if present
    if mention.wordidxs[-1] + 2 < len(sentence.words):
        mention.add_feature("NGRAM_RIGHT_2_[{}]".format(
            sentence.words[mention.wordidxs[-1] + 2].lemma))
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word in mention.words:
        for word2 in sentence.words:
            if word2.lemma in HPOTERM_KEYWORDS:
                p = sentence.get_word_dep_path(word.in_sent_idx,
                                               word2.in_sent_idx)
                mention.add_feature("KEYWORD_[" + word2.lemma + "]" + p)
                if len(p) < minl:
                    minl = len(p)
                    minp = p
                    minw = word2.lemma
    # Special feature for the keyword on the shortest dependency path
    if minw:
        mention.add_feature('EXT_KEYWORD_MIN_[' + minw + ']' + minp)
        mention.add_feature('KEYWORD_MIN_[' + minw + ']')
    # The labels and the NERs on the shortest dependency path
    # between a verb and the mention word.
    minl = 100
    minp = None
    minw = None
    for word in mention.words:
        for word2 in sentence.words:
            if word2.word.isalpha() and re.search('^VB[A-Z]*$', word2.pos) \
                    and word2.lemma != 'be':
                p = sentence.get_word_dep_path(word.in_sent_idx,
                                               word2.in_sent_idx)
                if len(p) < minl:
                    minl = len(p)
                    minp = p
                    minw = word2.lemma
        if minw:
            mention.add_feature('VERB_[' + minw + ']' + minp)


def extract(sentence):
    mentions = []
    # If there are no English words in the sentence, we skip it.
    no_english_words = True
    for word in sentence.words:
        word.stem = stemmer.stem(word.word)  # Here so all words have stem
        if len(word.word) > 2 and \
                (word.word in english_dict or
                 word.word.casefold() in english_dict):
            no_english_words = False
    if no_english_words:
        return mentions
    history = set()
    # Iterate over each phrase of length at most max_mention_length
    for start, end in get_all_phrases_in_sentence(sentence,
                                                  max_mention_length):
        if start in history or end - 1 in history:
            continue
        # The list of stems in the phrase (not from stopwords or symbols, and
        # not already used for a mention)
        phrase_stems = []
        for word in sentence.words[start:end]:
            if not re.match("^(_|\W)+$", word.word) and \
                    (len(word.word) == 1 or
                     word.word.casefold() not in stopwords_dict) and \
                    word.in_sent_idx not in history and word.stem in stems:
                phrase_stems.append(word.stem)
        phrase_stems_set = frozenset(phrase_stems)
        if len(phrase_stems_set) == 0:
            for i in range(start, end):
                history.add(i)
        max_ratio = 0.0
        max_entities = []
        max_words = dict()
        for hpo_name in inverted_hpoterms:
            stem_set = inverted_hpoterms[hpo_name]
            intersect = stem_set & phrase_stems_set
            if len(intersect) == 0 or \
                    not mandatory[stem_set].issubset(intersect) or \
                    ((len(stem_set) <= 4 or
                     len(stem_set - mandatory[stem_set]) <= 2) and
                     not stem_set <= phrase_stems_set) or \
                    len(intersect) <= MENTION_THRESHOLD * len(stem_set):
                continue
            else:
                # Find the word objects of that match
                mention_words = []
                mention_lemmas = []
                mention_stems = set()
                for word in sentence.words[start:end]:
                    if word.stem in stem_set and \
                            word.lemma.casefold() not in mention_lemmas and \
                            word.stem not in mention_stems:
                        mention_lemmas.append(word.lemma.casefold())
                        mention_words.append(word)
                        mention_stems.add(word.stem)
                        if len(mention_words) == len(stem_set):
                            break
                # Check whether the name contain words of a single letter. If
                # that is the case we want them to be immediately followed or
                # preceded in the mention by another word in the mention.
                should_continue = False
                is_previous_immediate = False
                is_next_immediate = False
                has_word_with_length_one = False
                for stem in stem_set:
                    if len(stem) == 1:
                        has_word_with_length_one = True
                        index = 0
                        while index < len(intersect):
                            if mention_words[index].stem == stem:
                                break
                            else:
                                index += 1
                        if index < len(mention_words)-1:
                            if mention_words[index+1].in_sent_idx == \
                                    mention_words[index].in_sent_idx + 1:
                                is_next_immediate = True
                        if index > 0:
                            if mention_words[index-1].in_sent_idx == \
                                    mention_words[index].in_sent_idx - 1:
                                is_previous_immediate = True
                        if has_word_with_length_one and \
                                not is_next_immediate and \
                                not is_previous_immediate:
                            should_continue = True
                            break
                if should_continue:
                    continue
                else:
                    ratio = len(intersect) / len(stem_set)
                    if ratio >= max_ratio:
                        max_ratio = ratio
                        max_entities.append(hpo_name)
                        max_words[hpo_name] = mention_words
        if max_ratio > 0.0:
            # Remove entities that are subsets of others
            to_remove = []
            for entity_1 in max_entities:
                intersect = inverted_hpoterms[entity_1] & phrase_stems_set
                for entity_2 in max_entities:
                    if entity_1 != entity_2 and \
                            inverted_hpoterms[entity_2] & phrase_stems_set <= \
                            intersect:
                        to_remove.append[entity_2]
            for entity in to_remove:
                max_entities.remove(entity)
            # We found one or more valid candidates, so create mentions
            for entity in max_entities:
                mention = Mention("HPOTERM", hponames_to_ids[entity] + "|" +
                                  entity, max_words[entity])
                add_features(mention, sentence)
                mentions.append(mention)
                for word in max_words[entity]:
                    history.add(word.in_sent_idx)
    if len(mentions) == 0 and random.random() <= NEG_PROB:
        index = random.randint(0, len(sentence.words) - 1)
        tries = 10
        while not sentence.words[index].lemma.isalpha() and tries > 0:
            index = random.randint(0, len(sentence.words) - 1)
            tries -= 1
        if sentence.words[index].lemma.isalpha():
            mention = Mention(
                "HPOTERM_SUP", sentence.words[index].lemma.casefold(),
                sentence.words[index:index+1])
            mention.is_correct = False
            add_features(mention, sentence)
            mentions.append(mention)
    return mentions


if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line,
                ["doc_id", "sent_id", "wordidxs", "words", "poses", "ners",
                    "lemmas", "dep_paths", "dep_parents", "bounding_boxes"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list])
            # Create the Sentence object
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Extract mention candidates
            mentions = extract(sentence)
            # Supervise
            new_mentions = supervise(mentions, sentence)
            # Print!
            for mention in new_mentions:
                print(mention.tsv_dump())
