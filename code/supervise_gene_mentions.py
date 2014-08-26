#! /usr/bin/env python3
#
# Perform distant supervision on gene mentions
#
# Each input row contains a mention and the sentence it is from
#

import fileinput
import json

from dstruct.Sentence import Sentence
from dstruct.Mention import Mention
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


# Load the dictionaries that we need
genes_dict = load_dict("genes")
english_dict = load_dict("english")
nih_grants_dict = load_dict("nih_grants")
nsf_grants_dict = load_dict("nsf_grants")
med_acrons_dict = load_dict("med_acrons")
pos_mentions_dict = load_dict("pos_gene_mentions")
neg_mentions_dict = load_dict("neg_gene_mentions")

# Process input
with fileinput.input() as input_files:
    for line in input_files:
        row = json.loads(line)
        sentence = Sentence(row["doc_id"], row["sent_id"], row["wordidxs"],
            row["sentence_words"], row["poses"], row["ners"], row["lemmas"],
            row["dep_paths"], row["dep_parents"], row["bounding_boxes"])
        mention = Mention(row["type"], row["entity"],
                sentence.words[row["start_word_idx"]:row["end_word_idx"]+1])
        # Perform supervision
        supervise(mention, sentence)
        # Print mention
        print(mention.json_dump())

