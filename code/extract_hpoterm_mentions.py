#! /usr/bin/env python3

import re

from dstruct.Mention import Mention
from helper.easierlife import get_input_sentences, get_all_phrases_in_sentence
from helper.dictionaries import load_dict

## Add features
def add_features(mention, sentence):
    # The word on the left of the mention, if present
    if mention.start_word_idx > 0:
        mention.add_feature("WINDOW_LEFT_1_with[{}]".format(sentence.words[mention.start_word_idx - 1].lemma))
    # The word on the right of the mention, if present
    if mention.end_word_idx + 1 < len(sentence.words):
        mention.add_features(["WINDOW_RIGHT_1_with[{}]".format(sentence.words[mention.end_word_idx + 1].lemma)])

# Yield mentions from the sentence
def extract(sentence):
    history = set()
    words = sentence.words
    for start, end in get_all_phrases_in_sentence(sentence, max_variant_length):
        if start in history or end in history:
                continue
        phrase = " ".join([word.word for word in words[start:end]])
        phrase_lower = phrase.lower()
        mention = None
        # If the phrase is in the dictionary, then is a possible mention
        if phrase_lower in hpoterms_dict:
            # Found a mention with this start and end: we can insert the
            # indexes of this mention in the history, and break the loop on
            # end and get to a new start
            for i in range(start, end + 1):
                history.add(i)
            term = hpoterms_dict[phrase_lower]
            mention = Mention("HPOTERM", term, words[start:end])
            mention.is_correct = True
            ## Add feature
            add_features(mention, sentence)
            yield mention

if __name__ == "__main":
    # Load the dictionaries that we need
    hpoterms_dict = load_dict("hpoterms")
    max_variant_length = 0
    for key in hpoterms_dict:
        length = len(key.split())
        if length > max_variant_length:
            max_variant_length = length

    # Process the input
    for sentence in get_input_sentences():
        for mention in extract(sentence):
            if mention:
                print(mention.json_dump())

