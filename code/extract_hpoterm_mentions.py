#! /usr/bin/env python3

import fileinput
import itertools
import math
import re

from nltk.stem.snowball import SnowballStemmer

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op
from helper.dictionaries import load_dict

MENTION_THRESHOLD = 3 / 4

HPOTERM_KEYWORDS = frozenset(
    ["syndrome", "gene", "association", "apoptosis", "genotype", "disease",
        "cancer", "carcinoma", "abnormality", "mutation", "protein",
        "diagnose", "patient", "patients", "viruses", "virus", "therapy",
        "symptom", "cronic,", "diagnosis", "detection", "severe", "phenotype",
        "affect", "genome", "genomic", "therapeutic", "pathway", "injury",
        "chromosome", "deletion", "polymorphism"])


# Perform the supervision
def supervise(mention, sentence):
    if "NO_ENGLISH_WORD_IN_SENTENCE" in mention.features:
        mention.is_correct = False
        return
    if "IS_EXACT_NAME" in mention.features:
        mention.is_correct = True
        return
    # if "HAS_ALL_STEMS" in mention.features:
    #    mention.is_correct = True
    #    return


# Add features
# TODO (Matteo) There are obviously many more missing
def add_features(mention, sentence):
    # There are no English words in the sentence
    # This may be useful to push down weird/junk sentences
    no_english_words = True
    for word in sentence.words:
        if len(word.word) > 2 and \
                (word.word in english_dict or
                 word.word.casefold() in english_dict):
            no_english_words = False
            break
    if no_english_words:
        mention.add_feature("NO_ENGLISH_WORDS_IN_SENTENCE")
        return
    if "NO_ENGLISH_WORDS_IN_SENTENCE" not in mention.features:
        # The lemma on the left of the mention, if present, provided it's
        # alphanumeric but not a number
        idx = mention.wordidxs[0] - 1
        while idx >= 0 and  \
                ((not sentence.words[idx].word.isupper() and
                  sentence.words[idx].lemma in stopwords_dict) and
                 not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word)
                 or len(sentence.words[idx].lemma) == 1):
            idx -= 1
        if idx >= 0:
            mention.left_lemma = sentence.words[idx].lemma
            mention.add_feature("WINDOW_LEFT_[{}]".format(
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
            mention.add_feature("WINDOW_RIGHT_[{}]".format(
                mention.right_lemma))
        # The word "two on the left" of the mention, if present
        if mention.wordidxs[0] > 1:
            mention.add_feature("WINDOW_LEFT_2_[{}]".format(
                sentence.words[mention.wordidxs[0] - 2].lemma))
        # The word "two on the right" on the left of the mention, if present
        if mention.wordidxs[-1] + 2 < len(sentence.words):
            mention.add_feature("WINDOW_RIGHT_2_[{}]".format(
                sentence.words[mention.wordidxs[-1] + 2].lemma))
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma in HPOTERM_KEYWORDS:
            p = sentence.get_word_dep_path(mention.wordidxs[0],
                                           word2.in_sent_idx)
            # mention.add_feature("KEYWORD_[" + word2.lemma + "]")
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    # Special feature for the keyword on the shortest dependency path
    if minw:
        mention.add_feature('EXT_KEYWORD_SHORTEST_PATH_[' + minw + ']' + minp)
        # mention.add_feature('KEYWORD_SHORTEST_PATH_[' + minw + ']')
    # The labels and the NERs on the shortest dependency path
    # between a verb and the mention word.
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.word.isalpha() and re.search('^VB[A-Z]*$', word2.pos) \
                and word2.lemma != 'be':
            p = sentence.get_word_dep_path(mention.wordidxs[0],
                                           word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw:
        mention.add_feature('EXT_VERB_PATH_[' + minw + ']' + minp)
    # There is no verb in the sentence
    # This may be useful to push down weird/junk sentences
    no_verb = True
    for word in sentence.words:
        if word.word.isalpha() and re.search('^VB[A-Z]*$', word.pos):
            no_verb = False
            break
    if no_verb:
        mention.add_feature("NO_VERB_IN_SENTENCE")
    mention_lemmas = set([x.lemma.casefold() for x in mention.words])
    name_words = set([x.casefold() for x in
                      mention.entity.split("|")[1].split()])
    if mention_lemmas == name_words:
        # The mention is exactly the hpo name
        mention.add_feature("IS_EXACT_NAME")
    else:
        mention_wordidxs = sorted(map(lambda x: x.in_sent_idx, mention.words))
        curr = mention_wordidxs[0]
        for i in mention_wordidxs[1:]:
            if i == curr + 1:
                curr = i
            else:
                break
        if curr == mention_wordidxs[-1]:
            mention.add_feature("WORDS_ARE_CONSECUTIVE")
        elif len(mention.words) == \
                len(inverted_hpoterms[mention.entity.split("|")[1]]):
            # The number of words in the mention is exactly the same as the
            # size of the complete set of stems for this entity
            mention.add_feature("HAS_ALL_STEMS")
        # The lemmas in the mention are a subset of the name
        if mention_lemmas.issubset(name_words):
            mention.add_feature("IS_SUBSET_OF_NAME")


# Add features that are related to the entire set of mentions candidates
def add_features_to_all(mentions, sentence):
    pass


# Return a list of mentions from the sentence
def extract(sentence):
    mentions = []
    # The list of stems in the sentence
    sentence_stems = []
    for word in sentence.words:
        word.stem = stemmer.stem(word.word)
        # Only add if it's not a symbol and not a stopword longer than 1.
        if not re.match("^(_|\W)+$", word.word) and \
                (len(word.word) == 1 or
                 word.word.casefold() not in stopwords_dict):
            sentence_stems.append(word.stem)
    sentence_stems_set = frozenset(sentence_stems)
    # Word indexes not already used for a mention
    sentence_available_word_indexes = set(
        [x.in_sent_idx for x in sentence.words])
    for pheno_stems in sorted_hpoterms:
        if pheno_stems.issubset(sentence_stems_set):
            # The following is the set of hpo_ids we added for this pheno_stems
            already_added = set()
            this_stem_set_mentions_words = dict()
            this_stem_set_mentions_stems = dict()
            for hpo_name in hpoterm_mentions_dict[pheno_stems]:
                # Find the word objects of this mention
                mention_words = []
                mention_stems = set()
                for word in sentence.words:
                    if word.stem in inverted_hpoterms[hpo_name] and \
                            word.lemma.casefold() not in \
                            [x.lemma.casefold() for x in mention_words] and \
                            word.in_sent_idx in \
                            sentence_available_word_indexes and \
                            word.stem not in mention_stems:
                        mention_words.append(word)
                        mention_stems.add(word.stem)
                this_stem_set_mentions_words[hpo_name] = mention_words
                this_stem_set_mentions_stems[hpo_name] = mention_stems
            keys = this_stem_set_mentions_words.keys()
            # Check whether the name contain words of a single letter. If that
            # is the case we want them to be immediately followed or preceded
            # in the mention by another word in the mention.
            for hpo_name in keys:
                for stem in inverted_hpoterms[hpo_name]:
                    if len(stem) == 1:
                        index = 0
                        while index < len(
                                this_stem_set_mentions_words[hpo_name]):
                            if this_stem_set_mentions_words[hpo_name][
                                    index].stem == stem:
                                break
                            else:
                                index += 1
                        is_next_immediate = False
                        if index < len(this_stem_set_mentions_words[hpo_name])\
                                - 1:
                            if this_stem_set_mentions_words[hpo_name][
                                    index+1].in_sent_idx == \
                                    this_stem_set_mentions_words[hpo_name][
                                    index].in_sent_idx + 1:
                                is_next_immediate = True
                        is_previous_immediate = False
                        if index > 0:
                            if this_stem_set_mentions_words[hpo_name][
                                    index-1].in_sent_idx == \
                                    this_stem_set_mentions_words[hpo_name][
                                    index].in_sent_idx - 1:
                                is_previous_immediate = True
                        if not is_next_immediate or not is_previous_immediate:
                            del this_stem_set_mentions_words[hpo_name]
                            del this_stem_set_mentions_stems[hpo_name]
            for hpo_name in sorted(
                    this_stem_set_mentions_words.keys(),
                    key=lambda x: len(this_stem_set_mentions_words[x]) /
                    len(inverted_hpoterms[x]),
                    reverse=True):
                words_to_remove = []
                for word in sentence.words:
                    if word.stem in sentence_stems and \
                            word in this_stem_set_mentions_words[hpo_name]:
                        # We used this word for this mention, so flag it to be
                        # removed from the list of words available for other
                        # possible mentions.
                        words_to_remove.append(word)
                        # Early termination
                        if len(words_to_remove) == \
                                len(this_stem_set_mentions_words[hpo_name]):
                            break
                # If the following test passes, we found all the words used by
                # this mention, which means that they weren't used by some
                # longer mentions, which is good and means we can create the
                # mention, as long as we haven't already created a mention with
                # the same hpo_id
                if len(words_to_remove) == \
                        len(this_stem_set_mentions_words[hpo_name]) and \
                        hponames_to_ids[hpo_name] not in already_added:
                    mention = Mention(
                        "HPOTERM", hponames_to_ids[hpo_name] + "|" + hpo_name,
                        this_stem_set_mentions_words[hpo_name])
                    mentions.append(mention)
                    already_added.add(hponames_to_ids[hpo_name])
                    add_features(mention, sentence)
                    # Remove the used words so they cannot be used by
                    # shorter mentions
                    for word in words_to_remove:
                        try:
                            sentence_stems.remove(word.stem)
                            sentence_available_word_indexes.remove(
                                word.in_sent_idx)
                        except:
                            pass
                    # Update as it may have changed
                    sentence_stems_set = frozenset(sentence_stems)
    return mentions


# Load the dictionaries that we need
english_dict = load_dict("english")
stopwords_dict = load_dict("stopwords")
hpoterms_dict = load_dict("hpoterms")
inverted_hpoterms = load_dict("hpoterms_inverted")
hponames_to_ids = load_dict("hponames_to_ids")
# hpodag = load_dict("hpoparents")

mandatory_stems = frozenset(
    ("keratocytosi", "carcinoma", "pancreat", "oropharyng", "hyperkeratos",
        "hyperkeratosi", "palmoplantar", "palmar", "genitalia", "labia",
        "hyperplasia", "fontanell", "facial", "prelingu", "sensorineur",
        "auditori", "neck", "incisor", "nervous", "ventricl", "cyst",
        "aplasia", "hypoplasia", "c-reactiv", "papillari",
        "beta-glucocerebrosidas"))

# Create the dictionary containing the sets of stems that we use to create the
# mentions
hpoterm_mentions_dict = dict()
for stem_set in hpoterms_dict:
    term_mandatory_stems = set()
    for stem in stem_set:
        if len(stem) == 1 or stem in mandatory_stems:
            term_mandatory_stems.add(stem)
    optional_stems = stem_set - term_mandatory_stems
    if len(stem_set) <= 4 or len(optional_stems) <= 2:
        if stem_set not in hpoterm_mentions_dict:
            hpoterm_mentions_dict[stem_set] = set()
        hpoterm_mentions_dict[stem_set] |= hpoterms_dict[stem_set]
    else:
        optional_subset_size = math.ceil(MENTION_THRESHOLD * len(stem_set)) - \
            len(term_mandatory_stems)
        for subset in itertools.combinations(
                optional_stems, optional_subset_size):
            subset = frozenset(term_mandatory_stems | set(subset))
            if subset not in hpoterm_mentions_dict:
                hpoterm_mentions_dict[subset] = set()
            hpoterm_mentions_dict[subset] |= hpoterms_dict[stem_set]
# Sort the keys in decreasing order according to length. This speeds up the
# extraction process
sorted_hpoterms = sorted(hpoterm_mentions_dict.keys(), key=len,
                         reverse=True)
# Initialize the stemmer
stemmer = SnowballStemmer("english")
if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            line_dict = get_dict_from_TSVline(
                line,
                ["doc_id", "sent_id", "wordidxs", "words", "poses", "ners",
                    "lemmas", "dep_paths", "dep_parents", "bounding_boxes"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list])
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            mentions = extract(sentence)
            for mention in mentions:
                if mention.type != "RANDOM":
                    supervise(mention, sentence)
                else:
                    # mention.add_feature("IS_RANDOM")
                    mention.is_correct = False
            if len(mentions) > 1:
                add_features_to_all(mentions, sentence)
            for mention in mentions:
                print(mention.tsv_dump())
