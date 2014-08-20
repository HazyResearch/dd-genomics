#! /usr/bin/env python3

import random
import sys
import re

from extractor.Extractor import MentionExtractor
from dstruct.GeneMention import GeneMention
from helper.easierlife import BASE_FOLDER

GENES_DICT_FILENAME="/dicts/hugo_synonyms.tsv"
ENGLISH_DICT_FILENAME="/dicts/english_words.tsv"
NIH_GRANTS_DICT_FILENAME="/dicts/grant_codes_nih.tsv"
MED_ACRONS_DICT_FILENAME="/dicts/med_acronyms_pruned.tsv"

NON_CORRECT_QUOTA = 100
NON_CORRECT_PROBABILITY = 0.1

class MentionExtractor_Gene(MentionExtractor):
    non_correct = 0

    def __init__(self):
        # Load the gene synonyms dictionary
        self.genes_dict = dict()
        with open(BASE_FOLDER + GENES_DICT_FILENAME, 'rt') as genes_dict_file:
            for line in genes_dict_file:
                tokens = line.strip().split("\t")
                # first token is name, the rest are synonyms
                name = tokens[0]
                for synonym in tokens:
                    self.genes_dict[synonym] = name
        # Load the English words dictionary
        # It's a set because it only contains a single column
        self.english_dict = set()
        with open(BASE_FOLDER + ENGLISH_DICT_FILENAME, 'rt') as english_dict_file:
            for line in english_dict_file:
                self.english_dict.add(line.rstrip().lower())
        # Load the NIH grant codes dictionary
        # It's a set because it only contains a single column
        self.nih_grants_dict = set()
        with open(BASE_FOLDER + NIH_GRANTS_DICT_FILENAME, 'rt') as nih_grants_dict_file:
            for line in nih_grants_dict_file:
                self.nih_grants_dict.add(line.rstrip().lower())
        # Load the medical abbreviation dictionary
        # It's a set because it only contains a single column
        self.med_acrons_dict = set()
        with open(BASE_FOLDER + MED_ACRONS_DICT_FILENAME, 'rt') as med_acrons_dict_file:
            for line in med_acrons_dict_file:
                self.med_acrons_dict.add(line.rstrip().lower())


    # Perform the distant supervision
    def supervise(self, sentence, mention):
        # Correct if it start with a letter and contains numbers and letters
        # mixed 
        # XXX (Matteo) No evidence
        if mention.symbol in self.genes_dict and \
            re.match("[A-Z]+[0-9]+[A-Z]+[0-9]*", mention.symbol):
            mention.is_correct = True
        if mention.symbol in self.genes_dict and \
            mention.symbol.lower() not in self.english_dict and \
            mention.symbol not in self.med_acrons_dict and \
            mention.symbol not in self.nih_grants_dict:
            mention.is_correct = True
        # Not correct if it's not in the dictionary of symbols and is an
        # English word
        elif mention.symbol not in self.genes_dict and mention.symbol.lower() in self.english_dict:
            mention.is_correct = False
        # Not correct if the previous word is one of the following
        # XXX (Matteo) Taken from pharm
        prev_word = sentence.get_prev_wordobject(mention)
        if prev_word != None and prev_word.word in ['Figure', 'Table', 'individual']:
                mention.is_correct = False


    # Yield mentions from sentence
    def extract(self, sentence):
        # Scan each word in the sentence
        for index in range(len(sentence.words)):
            mention = None
            word = sentence.words[index]
            # Very simple rule: if the word is in the dictionary, then is a
            # possible mention
            if word.word in self.genes_dict:
                mention = GeneMention(sentence.doc_id, word.word, [word,])
                self.supervise(sentence, mention)
            # Generate some negative examples
            elif self.non_correct < NON_CORRECT_QUOTA and random.random() < NON_CORRECT_PROBABILITY:
                self.non_correct += 1
                mention = GeneMention(sentence.doc_id, word.word, [word,])
                mention.is_correct = False

            # Add features
            if mention:
                if index > 0:
                    mention.add_features(["WINDOW_LEFT_1_with[{}]".format(sentence.words[index-1].lemma)])
                if index + 1 < len(sentence.words):
                    mention.add_features(["WINDOW_RIGHT_1_with[{}]".format(sentence.words[index + 1].lemma)])
                yield mention

