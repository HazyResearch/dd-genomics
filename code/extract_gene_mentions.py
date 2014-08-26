#! /usr/bin/env python3
#
# Extract gene mentions using the genes dictionary and add some features
#

import fileinput
import json
import random
import re
import sys

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.dictionaries import load_dict

# Perform the supervision
def supervise(mention, sentence):
    # If it's a gene symbol, and not an English word, and not a medical
    # acronym, and not a NIH or NSF grant code, then label it as correct
    # Taken from pharm
    mention_word = mention.words[0].word
    if mention_word in genes_dict and \
        mention_word.lower() not in english_dict and \
        mention_word not in med_acrons_dict and \
        mention_word not in nih_grants_dict and\
        mention_word not in nsf_grants_dict:
            mention.is_correct = True
    # Not correct if the previous word is one of the following keywords.
    # Taken from pharm
    prev_word = sentence.get_prev_wordobject(mention)
    if prev_word != None and prev_word.word.lower() in ['figure', 'table', 'individual', "figures", "tables", "individuals"]:
        mention.is_correct = False
    # Not correct if it is in our collection of positive examples
    if frozenset([sentence.doc_id, str(sentence.sent_id), mention_word]) in pos_mentions_dict:
        mention.is_correct = True
    # Not correct if it is in our collection of negative examples
    if frozenset([sentence.doc_id, str(sentence.sent_id), mention_word]) in neg_mentions_dict:
        mention.is_correct = False
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
    if re.match("[A-Z]+[0-9]+[A-Z]+[0-9]*", mention.words[0].word):
        mention.add_feature('IS_MIX_OF_LETTERS_NUMBERS_LETTERS')
    # The symbol is a mix of letters and numbers (can end with a number)
    if re.match("[A-Z]+[0-9]+", mention.words[0].word):
        mention.add_feature('IS_MIX_OF_LETTERS_NUMBERS')
    # The word is in the English dictionary
    if mention.words[0].word in english_dict:
        mention.add_feature('IS_ENGLISH_WORD')
    # The word comes after an organization, or a location, or a person
    comes_after = None
    if mention.start_word_idx > 0 and sentence.words[mention.start_word_idx - 1].ner in [ "ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("COMES_AFTER_" + sentence.words[mention.start_word_idx - 1].ner)
        comes_after = sentence.words[mention.start_word_idx - 1].ner
    # The word comes before an organization, or a location, or a person
    comes_before = None
    if mention.start_word_idx < len(sentence.words) - 1 and sentence.words[mention.start_word_idx + 1].ner in [ "ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("COMES_BEFORE_" + sentence.words[mention.start_word_idx - 1].ner)
        comes_before = sentence.words[mention.start_word_idx - 1].ner
    # The word is between two words that are an organization, or a location or a person
    if comes_before and comes_after:
        mention.add_feature("IS_BETWEEN_" + comes_after + "_" + comes_before)
    # The word comes after a "document element" (e.g., table, or figure)
    prev_word = sentence.get_prev_wordobject(mention)
    if prev_word != None and prev_word.word.lower() in ['figure', 'table', 'individual', "figures", "tables", "individuals"]:
        mention.add_feature("IS_AFTER_DOC_ELEMENT")
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
    # The word appears many times (more than 3) in the sentence
    if [w.word for w in sentence.words].count(mention.words[0].word) > 3:
        mention.add_feature("APPEARS_MANY_TIMES_IN_SENTENCE")

# Yield mentions from the sentence
def extract(sentence):
    global created_examples
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
        elif word.word.isalnum() and word.word not in stopwords_dict and \
                not word.pos.startswith("VB") and \
                random.random() < example_prob and created_examples < examples_quota:
            # Generate a mention that somewhat resembles what a gene may look like,
            # or at least its role in the sentence.
            mention = Mention("RANDOM", word.word, [word,])
            # Add features
            add_features(mention, sentence)
            mention.is_correct = False
            created_examples += 1
            yield mention

# Load the dictionaries that we need
genes_dict = load_dict("genes")
english_dict = load_dict("english")
nih_grants_dict = load_dict("nih_grants")
nsf_grants_dict = load_dict("nsf_grants")
med_acrons_dict = load_dict("med_acrons")
stopwords_dict = load_dict("stopwords")
pos_mentions_dict = load_dict("pos_gene_mentions")
neg_mentions_dict = load_dict("neg_gene_mentions")


if __name__ == "__main__":
    # Get arguments
    if len(sys.argv) < 3:
        sys.stderr.write("{}: ERROR: wrong number of arguments\n".format(os.path.basename(sys.argv[0])))
        sys.exit(1)
    examples_quota = int(sys.argv[1])
    example_prob = float(sys.argv[2])
    created_examples = 0
    # Process the input
    with fileinput.input(sys.argv[3:]) as f:
        for line in f:
            line_dict = json.loads(line)
            sentence = Sentence(line_dict["doc_id"], line_dict["sent_id"],
                    line_dict["wordidxs"], line_dict["words"],
                    line_dict["poses"], line_dict["ners"], line_dict["lemmas"],
                    line_dict["dep_paths"], line_dict["dep_parents"],
                    line_dict["bounding_boxes"])
            for mention in extract(sentence):
                if mention:
                    if "acronym" in line_dict:
                        if mention.words[0].word == line_dict["acronym"]:
                            mention.type = "ACRONYM"
                            mention.is_correct = False
                    else:
                        # Perform supervision
                        supervise(mention, sentence)
                    print(mention.json_dump())

