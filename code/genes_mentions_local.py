#! /usr/bin/env python3
#
# Find mentions of genes in a 'local' way (i.e., in a sentence-level way) by
# looking up words in the gene synonyms dictionary
#
# First argument is the application base directory
#

import random
import json
import sys

# Type of the mentions
MENTION_TYPE="GENE"

# Number of non correct mentions to generate
NON_CORRECT_QUOTA = 100
# Probabily of generating a non correct mention
NON_CORRECT_PROBABILITY = 0.7

# Load the gene synonyms dictionary
GENES_DICT_FILENAME="/dicts/hugo_synonyms.tsv"
genes_dict = dict()
with open(sys.argv[1] + GENES_DICT_FILENAME, 'rt') as genes_dict_file:
    for line in genes_dict_file:
        tokens = line.strip().split("\t")
        # first token is name, the rest are synonyms
        name = tokens[0]
        for synonym in tokens:
            genes_dict[synonym] = name


# Process input
non_correct = 0
for _row in sys.stdin:
    row = json.loads(_row)
    doc_id = row["docid"]
    sent_id = row["sentid"]
    wordidxs = row["wordidxs"]
    words = row["words"]
    poses = row["poses"]
    ners = row["ners"]
    lemmas = row["lemmas"]
    dep_paths = row["dep_paths"]
    dep_parents = row["dep_parents"]
    bounding_boxes = row["bounding_boxes"]

    # Very simple rule: if the word is in the dictionary, then is a mention
    for index in range(len(words)):
        word = words[index]
        if word in genes_dict:
            provenance = [ doc_id, sent_id, index, index, word]
            mention_id = "_".join(str(x) for x in (doc_id, sent_id, index, index))
            name = genes_dict[word]
            
            print(json.dumps({"id": None, "mention_id": mention_id,
                "provenance": provenance, "name": name, "is_correct": True,
                "features": [dep_parents[index]]}))
        # generate negative example
        elif non_correct < NON_CORRECT_QUOTA and random.random() < NON_CORRECT_PROBABILITY:
            non_correct += 1
            provenance = [ doc_id, sent_id, index, index, word]
            mention_id = "_".join(str(x) for x in (doc_id, sent_id, index, index))
            name = lemmas[index]
            
            print(json.dumps({"id": None, "mention_id": mention_id,
                "provenance": provenance, "name": name, "is_correct": False,
                "features": [dep_parents[index]]}))

            

