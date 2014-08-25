#! /usr/bin/env python3
#
# Extract gene mentions using the genes dictionary and add some features
#
# XXX ATTENTION: This script does _NOT_ perform distant supervision
#

import re

from dstruct.Mention import Mention
from helper.easierlife import get_input_sentences
from helper.dictionaries import load_dict

## Add features to a gene mention
def add_features(mention, sentence):
    # The NER is an organization, or a location, or a person
    if mention.words[0].ner in [ "ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("IS_" + mention.words[0].ner)
    # The POS is a proper noun
    if mention.words[0].pos in ["NNP",]:
        mention.add_feature("IS_NNP")
    # The symbol is a mix of letters and numbers (but can't be only
    # letters followed by numbers)
    if re.match("[A-Z]+[0-9]+[A-Z]+[0-9]*", mention.entity):
        mention.add_feature('IS_MIX_OF_LETTERS_NUMBERS_LETTERS')
    # The symbol is a mix of letters and numbers (can end with a number)
    if re.match("[A-Z]+[0-9]+", mention.entity):
        mention.add_feature('IS_MIX_OF_LETTERS_NUMBERS')
    # The labels and the NERs on the shortest dependency path
    # between a verb and the mention word.
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.pos.startswith('V') and word2.lemma != 'be':
            p = sentence.get_word_dep_path(mention.start_word_idx, word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw != None:
        mention.add_feature('VERB_PATH_[' + minw + '] '+ minp)
    # The labels and the NERs on the shortest dependency path
    # between a keyword and the mention word
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma in ["gene", "genes", "protein", "proteins"]:
            p = sentence.get_word_dep_path(mention.start_word_idx, word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw != None:
        mention.add_feature('KEYWORD_PATH_[' + minw + '] ' + minp)
    # The lemma on the left of the mention, if present
    if mention.start_word_idx > 0:
        mention.add_feature("WINDOW_LEFT_1_[{}]".format(
            sentence.words[mention.start_word_idx - 1].lemma))
    # The word on the right of the mention, if present
    if mention.end_word_idx + 1 < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_1_[{}]".format(
            sentence.words[mention.end_word_idx + 1].lemma))

# Yield mentions from the sentence
def extract(sentence):
    # Scan each word in the sentence
    for index in range(len(sentence.words)):
        mention = None
        word = sentence.words[index]
        # If the word is in the dictionary, then is a possible mention
        if word.word in genes_dict:
            mention = Mention("GENE", genes_dict[word.word], [word,])
            # Add features
            add_features(mention, sentence)
            yield mention

# Load the dictionaries that we need
genes_dict = load_dict("genes")
english_dict = load_dict("english")
nih_grants_dict = load_dict("nih_grants")
nsf_grants_dict = load_dict("nsf_grants")
med_acrons_dict = load_dict("med_acrons")
pos_mentions_dict = load_dict("pos_gene_mentions")
neg_mentions_dict = load_dict("neg_gene_mentions")

# Process the input
for sentence in get_input_sentences():
    for mention in extract(sentence):
        if mention:
            print(mention.json_dump())

