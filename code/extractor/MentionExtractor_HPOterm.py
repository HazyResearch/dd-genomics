#! /usr/bin/env python3

import random
import sys
import re

from extractor.Extractor import MentionExtractor
from dstruct.HPOtermMention import HPOtermMention
from helper.easierlife import BASE_FOLDER, get_all_phrases_in_sentence

HPOTERMS_DICT_FILENAME="/dicts/hpo_terms.tsv"

NON_CORRECT_QUOTA = 100
NON_CORRECT_PROBABILITY = 0.1

# XXX (Matteo) This function should probably be in helper.easierlife
# Given a list of words, return a list of variants built by splitting words
# that contain the separator.
# An example is more valuable:
# let words = ["the", "cat/dog", "is", "mine"], the function would return ["the
# cat is mine", "the doc is mine"]
def get_variants(words, separator="/"):
    if len(words) == 0:
        return []
    variants = []
    base = []
    i = 0
    # Look for a word containing a "/"
    while words[i].find(separator) == -1:
        base.append(words[i])
        i += 1
        if i == len(words):
            break
    # If we found a word containing a "/", call recursively
    if i < len(words):
        variants_starting_words = words[i].split("/")
        following_variants = get_variants(words[i+1:])
        for variant_starting_word in variants_starting_words:
            variant_base = base + [variant_starting_word]
            if len(following_variants) > 0:
                for following_variant in following_variants:
                    variants.append(" ".join(variant_base +[following_variant]))
            else:
                variants.append(" ".join(variant_base))
    else:
        variants = [" ".join(base)]
    return variants
 

class MentionExtractor_HPOterm(MentionExtractor):
    non_correct = 0

    def __init__(self):
        # Load the HPO terms dictionary
        self.hpoterms_dict = dict()
        self.max_variant_length = 0 # No. of words in longest variant
        with open(BASE_FOLDER + HPOTERMS_DICT_FILENAME, 'rt') as hpoterms_dict_file:
            for line in hpoterms_dict_file:
                tokens = line.strip().split("\t")
                # 1st token is name, 2nd is description, 3rd is 'C' and 4th is
                # (presumably) the distance from the root of the DAG.
                name = tokens[0]
                description = tokens[1]
                description_words = description.split()
                variants = get_variants(description_words)
                for variant in variants:
                    if len(variant.split()) > self.max_variant_length:
                        self.max_variant_length = len(variant.split())
                    self.hpoterms_dict[variant.lower()] = name

    def supervise(self):
        pass

    def extract(self, sentence):
        history = set()
        words = sentence.words
        for start, end in get_all_phrases_in_sentence(sentence, self.max_variant_length):
            if start in history or end in history:
                    continue
                
            phrase = " ".join([word.word for word in words[start:end]])
            phrase_lower = phrase.lower()

            # Very simple rule: if the phrase is in the dictionary, then is a mention
            if phrase_lower in self.hpoterms_dict:
                # Found a mention with this start and end: we can insert the
                # indexes of this mention in the history, and break the loop on
                # end and get to a new start
                for i in range(start, end + 1):
                    history.add(i)
                break
                term = self.hpoterms_dict[phrase_lower]
                mention = HPOtermMention(sentence.doc_id, term, words[start:end])
                mention.is_correct = True
                mention.add_features([]) # XXX TODO
            elif self.non_correct < NON_CORRECT_QUOTA and random.random() < NON_CORRECT_PROBABILITY:
                self.non_correct += 1
                mention = HPOtermMention(sentence.doc_id, "NONCORRECT", words[start:end])
                mention.is_correct = False
                mention.add_features([]) # XXX TODO
                yield mention

