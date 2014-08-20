#! /usr/bin/env python3

import random
import sys
import re

from extractor.Extractor import MentionExtractor
from dstruct.GeneMention import GeneMention
from helper.easierlife import BASE_FOLDER

GENES_DICT_FILENAME="/dicts/hugo_synonyms.tsv"

NON_CORRECT_QUOTA = 100
NON_CORRECT_PROBABILITY = 0.1

class MentionExtractor_Gene(MentionExtractor):
    non_correct = 0

    def __init__(self):
        # Load the gene synonyms dictionary
        self.genes_dict = dict()
        with open(BASE_FOLDER + GENES_DICT_FILENAME, 'rt') as self.genes_dict_file:
            for line in self.genes_dict_file:
                tokens = line.strip().split("\t")
                # first token is name, the rest are synonyms
                name = tokens[0]
                for synonym in tokens:
                    self.genes_dict[synonym] = name

    def supervise(self, mention):
        # TODO (Matteo): Human genes are spelled all capital (source: Amir, 20140819)
        pass

    def extract(self, sentence):
        # Very simple rule: if the word is in the dictionary, then is a mention
        for word in sentence.words:
            if word.word in self.genes_dict:
                mention = GeneMention(sentence.doc_id, word.word, [word,])
                mention.is_correct = True
                mention.add_features([word.word])
                yield mention
                
            elif self.non_correct < NON_CORRECT_QUOTA and random.random() < NON_CORRECT_PROBABILITY:
                self.non_correct += 1
                mention = GeneMention(sentence.doc_id, word.word, [word,])
                mention.is_correct = False
                mention.add_features([word.word])
                yield mention

