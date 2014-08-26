#! /usr/bin/env python3
#
# Create some random background mentions labeled as is_correct=False for
# learning the genes mentions
#
# The first two arguments of this script are the maximum number of examples to
# generate and with which probability an word is chosen as an example.

import os.path
import random
import sys

from dstruct.Mention import Mention
from extract_gene_mentions import add_features
from helper.dictionaries import load_dict
from helper.easierlife import get_input_sentences

# Load the dictionaries that we need
genes_dict = load_dict("genes")
stopwords_dict = load_dict("stopwords")
english_dict = load_dict("english")

# Yield random mentions labeled as non correct
def extract(sentence):
    global created
    # Scan each word in the sentence
    for index in range(len(sentence.words)):
        mention = None
        word = sentence.words[index]
        # Generate a mention that somewhat resembles what a gene may look like,
        # or at least its role in the sentence.
        if word.word.isalnum() and word.word not in stopwords_dict and \
                not word.pos.startswith("VB") and \
                random.random() < example_prob and created < examples_quota:
            mention = Mention("RANDOM", word.word, [word,])
            # Add features
            add_features(mention, sentence)
            mention.is_correct = False
            created += 1
            yield mention
        if created == examples_quota:
            sys.exit(0)

# Get arguments
if len(sys.argv) < 3:
    sys.stderr.write("{}: ERROR: wrong number of arguments\n".format(os.path.basename(sys.argv[0])))
    sys.exit(1)
examples_quota = int(sys.argv[1])
example_prob = float(sys.argv[2])

# Process the input
created = 0
for sentence in get_input_sentences(sys.argv[3:]):
    for mention in extract(sentence):
        if mention:
            print(mention.json_dump())

