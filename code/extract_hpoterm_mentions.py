#! /usr/bin/env python3

import fileinput
import math
import random
import re

from nltk.stem.snowball import SnowballStemmer

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op
from helper.dictionaries import load_dict

MENTION_THRESHOLD = 2 / 3
SUPERVISION_HPOTERMS_DICT_FRACTION = 0.5
SUPERVISION_PROB = 0.5
RANDOM_EXAMPLES_PROB = 0.01
RANDOM_EXAMPLES_QUOTA = 7500
random_examples = 0

HPOTERM_KEYWORDS = frozenset(
    ["syndrome", "gene", "association", "apoptosis", "genotype", "disease",
        "cancer", "carcinoma", "abnormality", "mutation", "protein",
        "diagnose", "patient", "patients", "viruses", "virus", "therapy",
        "symptom", "cronic,", "diagnosis", "detection", "severe", "phenotype",
        "affect", "genome", "genomic", "therapeutic", "pathway", "injury",
        "chromosome", "deletion", "polymorphism"])


# Perform the supervision
def supervise(mention, sentence):
    if random.random() < SUPERVISION_PROB and \
            " ".join([x.word.casefold() for x in mention.words]) in \
            supervision_hpoterms_dict:
        mention.is_correct = True


# Add features
# TODO (Matteo) There are obviously many more missing
def add_features(mention, sentence):
    # The word "two on the left" of the mention, if present
    if mention.wordidxs[0] > 1:
        mention.add_feature("WINDOW_LEFT_2_[{}]".format(
            sentence.words[mention.wordidxs[0] - 2].lemma))
    # The word "two on the right" on the left of the mention, if present
    if mention.wordidxs[-1] + 2 < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_2_[{}]".format(
            sentence.words[mention.wordidxs[-1] + 2].lemma))
    # The word on the left of the mention, if present
    if mention.wordidxs[0] > 0:
        mention.add_feature("WINDOW_LEFT_1_[{}]".format(
            sentence.words[mention.wordidxs[0] - 1].lemma))
    # The word on the right of the mention, if present
    if mention.wordidxs[-1] + 1 < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_1_[{}]".format(
            sentence.words[mention.wordidxs[-1] + 1].lemma))
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma in HPOTERM_KEYWORDS:
            p = sentence.get_word_dep_path(mention.wordidxs[0],
                                           word2.in_sent_idx)
            mention.add_feature("KEYWORD_[" + word2.lemma + "]")
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    # Special feature for the keyword on the shortest dependency path
    if minw:
        mention.add_feature('EXT_KEYWORD_SHORTEST_PATH_[' + minw + ']' + minp)
        mention.add_feature('KEYWORD_SHORTEST_PATH_[' + minw + ']')
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
        mention.add_feature('VERB_PATH_[' + minw + ']')
    # There is no verb in the sentence
    # This may be useful to push down weird/junk sentences
    no_verb = True
    for word in sentence.words:
        if re.search('^VB[A-Z]*$', word.pos):
            no_verb = False
            break
    if no_verb:
        mention.add_feature("NO_VERB_IN_SENTENCE")


# Add features that are related to the entire set of mentions candidates
def add_features_to_all(mentions, sentence):
    # Number of other mentions in the sentence
    for i in range(1, len(mentions)):
        for mention in mentions:
            mention.add_feature("{}_OTHER_MENTIONS_IN_SENTENCE".format(i))


# Return a list of mentions from the sentence
def extract(sentence):
    global random_examples
    mentions = []
    sentence_stems = set()
    for word in sentence.words:
        if word.word.casefold() not in stopwords_dict:
            sentence_stems.add(stemmer.stem(word.word))
    possible_mentions = set()
    for pheno_stems in hpoterms_dict:
        intersect_size = len(sentence_stems.intersection(pheno_stems))
        if intersect_size > math.ceil(MENTION_THRESHOLD * len(pheno_stems)):
            to_add = True
            to_remove = []
            for mention in possible_mentions:
                if pheno_stems.issubset(mention):
                    to_add = False
                    break
                elif pheno_stems.issuperset(mention):
                    to_remove.append(mention)
                else:  # do nothing
                    pass
            for mention in to_remove:
                possible_mentions.remove(mention)
            if to_add:
                possible_mentions.add(pheno_stems)
    # Create the mention objects for the possible mentions
    for possible_mention in possible_mentions:
        leftovers = set(possible_mention)
        mention_words = []
        for word in sentence.words:
            stem = stemmer.stem(word.word)
            if stem in possible_mention:
                mention_words.append(word)
                if stem in leftovers:
                    leftovers.remove(stemmer.stem(word.word))
                    if len(leftovers) == 0:
                        break
        name = hpoterms_dict[possible_mention]
        mention = Mention("HPOTERM", "|".join(name), mention_words)
        mentions.append(mention)
    if len(mentions) == 0:
        # Potentially generate a random mention that resembles real ones
        # This mention is supervised (as false) in the code calling this
        # function
        # XXX (Matteo) may need additional conditions to generate a mention
        if random.random() < RANDOM_EXAMPLES_PROB and \
                random_examples < RANDOM_EXAMPLES_QUOTA \
                and len(sentence.words) > 1:
            start, end = random.sample(range(len(sentence.words)), 2)
            if start > end:
                tmp = end
                start = end
                end = tmp
            if end - start > 1:
                mention = Mention(
                    "RANDOM", "random", sentence.words[start:end])
                random_examples += 1
                # Add features
                add_features(mention, sentence)
                mentions.append(mention)
    return mentions


# Load the dictionaries that we need
stopwords_dict = load_dict("stopwords")
hpoterms_dict = load_dict("hpoterms")
# Create supervision dictionary that only contains a fraction of the genes in
# the gene dictionary. This is to avoid that we label as positive examples
# everything that is in the dictionary
supervision_hpoterms_dict = dict()
to_sample = set(random.sample(range(
    len(hpoterms_dict)), int(
        len(hpoterms_dict) * SUPERVISION_HPOTERMS_DICT_FRACTION)))
i = 0
for hpoterm in hpoterms_dict:
    if i in to_sample:
        supervision_hpoterms_dict[hpoterm] = hpoterms_dict[hpoterm]
    i += 1

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
            for mention in extract(sentence):
                if mention.type != "RANDOM":
                    supervise(mention, sentence)
                else:
                    # mention.add_feature("IS_RANDOM")
                    mention.is_correct = False
            if len(mentions) > 1:
                add_features_to_all(mentions, sentence)
            for mention in mentions:
                print(mention.tsv_dump())
