#! /usr/bin/env python3
#
# Extract gene mention candidates, add features, and
# perform distant supervision
#

import fileinput
import json
import random
import re
import sys

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.dictionaries import load_dict

SUPERVISION_GENES_DICT_FRACTION = 0.3
EXAMPLES_PROB = 0.01
EXAMPLE_QUOTA = 15000
created_examples = 0

## Perform the supervision
def supervise(mention, sentence):
    # If the candidate mention a gene symbol in the supervision dictionary, and
    # not an English word, and not a medical acronym, and not a NIH or NSF
    # grant code, and not a Roman numeral then label it as correct 
    mention_word = mention.words[0].word
    if mention_word in supervision_genes_dict and \
        mention_word.lower() not in english_dict and \
        mention_word not in med_acrons_dict and \
        mention_word not in nih_grants_dict and \
        mention_word not in nsf_grants_dict and \
        not re.match("^(IV|VI{,3}|I{1,4})$", mention_word):
            mention.is_correct = True
    # Not correct if the previous word is one of the following keywords.
    prev_word = sentence.get_prev_wordobject(mention)
    if prev_word != None and prev_word.word.lower() in ['figure', 'table',
            'individual', "individuals","figures", "tables", "fig", "fig.",
            "figs", "figs."]:
        mention.is_correct = False
    # Not correct if it is in our collection of positive examples
    if frozenset([sentence.doc_id, str(sentence.sent_id), mention_word]) in pos_mentions_dict:
        mention.is_correct = True
    # Not correct if it is in our collection of negative examples
    if frozenset([sentence.doc_id, str(sentence.sent_id), mention_word]) in neg_mentions_dict:
        mention.is_correct = False
    # If the sentence is contains less than 3 words, it probably doesn't have
    # enough information to convey anything.
    if len(sentence.words) < 3:
        mention.is_correct = False


## Add features to a gene mention
def add_features(mention, sentence):
    # Is in the genes dictionary
    if mention.words[0].word in genes_dict:
        mention.add_feature("IS_IN_GENE_DICTIONARY")
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
        if word2.pos.startswith('VB') and word2.lemma != 'be':
            p = sentence.get_word_dep_path(mention.start_word_idx, word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw != None:
        mention.add_feature('EXT_VERB_PATH_[' + minw + ']' + minp)
        mention.add_feature('VERB_PATH_[' + minw + ']')
    # The labels and the NERs on the shortest dependency path
    # between a keyword and the mention word
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma in ["gene", "genes", "protein", "proteins", "DNA", "rRNA"]:
            p = sentence.get_word_dep_path(mention.start_word_idx, word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw != None:
        mention.add_feature('EXT_KEYWORD_PATH_[' + minw + ']' + minp)
        mention.add_feature('KEYWORD_PATH_[' + minw + ']')
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


## Yield mentions from the sentence
def extract(sentence):
    global created_examples
    # Scan each word in the sentence
    for index in range(len(sentence.words)):
        mention = None
        word = sentence.words[index]
        # If the word satisfies the regex, or is in the dictionary, then is a
        # mention candidate.
        if word.word in genes_dict or \
                re.match("[A-Z]+[0-9]+[A-Z]*", word.word):
            mention = Mention("GENE", genes_dict[word.word], [word,])
            # Add features
            add_features(mention, sentence)
            yield mention
        else: # Potentially generate a random mention
            # Check whether it's a number, we do not want to generate a mention
            # with it.
            try:
                float(word.word)
            except:
                is_number = False
            else:
                is_number = True
            if word.word.isalnum() and not is_number and word.word not in stopwords_dict and \
                not word.pos.startswith("VB") and \
                random.random() < EXAMPLES_PROB and created_examples < EXAMPLES_QUOTA:
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

# Create supervision dictionary that only contains a fraction of the genes in the gene
# dictionary. This is to avoid that we label as positive examples everything
# that is in the dictionary
supervision_genes_dict = dict()
to_sample = set(random.sample(range(len(supervision_genes_dict.keys)),
        len(supervision_genes_dict.keys)  ))
i = 0
for gene in genes_dict:
    if i in to_sample:
        supervision_genes_dict[gene] = genes_dict[gene]
    i += 1

if __name__ == "__main__":
    # Process the input
    with fileinput.input() as f:
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

