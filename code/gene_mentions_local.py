#! /usr/bin/env python3
#
# Find mentions of genes in a 'local' way (i.e., in a sentence-level way) by
# looking up words in the gene synonyms dictionary
#
# First argument is the application base directory
#


import json
import sys

# Type of the mentions
MENTION_TYPE="GENE"

# Load the gene synonyms dictionary
GENES_DICT_FILENAME="dict/hugo_synonyms.tsv"
genes_dict = dict()
with open(sys.argv[1] + GENES_DICT_FILENAME, 'rt') as genes_dict_file:
    for line in genes_dict_file:
        tokens = line.strip().split("\t")
        # first token is name, the rest are synonyms
        name = tokens[0]
        for synonym in tokens:
            genes_dict[synonym] = name


# Process input
for _row in sys.stdin:
    row = json.loads(_row)
    doc_id = row["docid"]
    sent_id = row["sentid"]
    wordidxs = row["wordidixs"]
    words = row["words"]
    poses = row["poses"]
    ners = row["nerds"]
    lemmas = row["lemma"]
    dep_paths = row["dep_paths"]
    dep_parents = row["dep_parents"]
    bounding_boxes = row["bounding_boxes"]

    # Very simple rule: if the word is in the dictionary, then is a mention
    for index in len(words):
        word = words[index]
        if word in genes_dict:
            provenance = [ doc_id, sent_id, index, index, word]
            mention_id = "_".join([doc_id, sent_id, index, index])
            name = genes_dict[word]
            
            print(json.dumps({"id": None, "mention_id": mention_id,
                "provenance": provenance, "name": name}))

