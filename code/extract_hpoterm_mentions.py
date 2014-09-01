#! /usr/bin/env python3

import random

from dstruct.Mention import Mention
from helper.easierlife import get_input_sentences, get_all_phrases_in_sentence
from helper.dictionaries import load_dict

SUPERVISION_HPOTERMS_DICT_FRACTION = 0.3
SUPERVISION_PROB = 0.5
RANDOM_EXAMPLES_PROB = 0.01
RANDOM_EXAMPLES_QUOTA = 15000
random_examples = 0

## Perform the supervision
def supervise(mention, sentence):
    if random.random() < SUPERVISION_PROB and \
            " ".join([x.word.casefold() for x in mention.words]) in supervision_hpoterms_dict:
        mention.is_correct = True


## Add features
# TODO (Matteo) There are obviously many more missing
def add_features(mention, sentence):
    # The word "two on the left" of the mention, if present
    if mention.wordidxs[0] > 1:
        mention.add_feature("WINDOW_LEFT_2_[{}]".format(sentence.words[mention.wordidxs[0] - 2]))
    # The word "two on the right" on the left of the mention, if present
    if mention.wordidxs[-1] + 2 < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_2_[{}]".format(sentence.words[mention.wordidxs[-1] + 2]))
    # The word on the left of the mention, if present
    if mention.wordidxs[0] > 0:
        mention.add_feature("WINDOW_LEFT_1_[{}]".format(sentence.words[mention.wordidxs[0] - 1].lemma))
    # The word on the right of the mention, if present
    if mention.wordidxs[-1] + 1 < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_1_[{}]".format(sentence.words[mention.wordidxs[-1] + 1].lemma))


## Return a list of mentions from the sentence
def extract(sentence):
    global random_examples
    mentions = []
    history = set()
    words = sentence.words
    for start, end in get_all_phrases_in_sentence(sentence, max_variant_length):
        if start in history or end in history:
                continue
        phrase = " ".join([word.word for word in words[start:end]])
        phrase_caseless = phrase.casefold()
        mention = None
        # If the phrase is in the dictionary, then is a possible mention
        if phrase_caseless in hpoterms_dict:
            # Found a mention with this start and end: we can insert the
            # indexes of this mention in the history, and break the loop on
            # end and get to a new start
            for i in range(start, end + 1):
                history.add(i)
            term = hpoterms_dict[phrase_caseless]
            mention = Mention("HPOTERM", term, words[start:end])
            # Add feature
            add_features(mention, sentence)
            mentions.append(mention)
        else: 
            # Potentially generate a random mention that resembles real ones
            # This mention is supervised (as false) in the code calling this function
            # XXX (Matteo) may need additional conditions to generate a mention
            if random.random() < RANDOM_EXAMPLES_PROB and random_examples < RANDOM_EXAMPLES_QUOTA:
                mention = Mention("RANDOM", "random", words[start:end])
                random_examples += 1
                mentions.append(mention)
    return mentions


# Load the dictionaries that we need
hpoterms_dict = load_dict("hpoterms")
# Create supervision dictionary that only contains a fraction of the genes in the gene
# dictionary. This is to avoid that we label as positive examples everything
# that is in the dictionary
supervision_hpoterms_dict = dict()
to_sample = set(random.sample(range(len(hpoterms_dict)),
        int(len(hpoterms_dict) * SUPERVISION_HPOTERMS_DICT_FRACTION)))
i = 0
for hpoterm in hpoterms_dict:
    if i in to_sample:
        supervision_hpoterms_dict[hpoterm] = hpoterms_dict[hpoterm]
    i += 1


if __name__ == "__main__":
    max_variant_length = 0
    for key in hpoterms_dict:
        length = len(key.split())
        if length > max_variant_length:
            max_variant_length = length
    # Process the input
    for sentence in get_input_sentences():
        for mention in extract(sentence):
            if mention.type != "RANDOM":
                supervise(mention, sentence)
            else:
                mention.is_correct = False
            print(mention.json_dump())

