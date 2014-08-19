#! /usr/bin/env python3
#
#

import json
import sys

# Type of the mentions
MENTION_TYPE="HPOTERM"

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


# Load the HPO terms dictionary
HPOTERMS_DICT_FILENAME="/dicts/hpo_terms.tsv"
hpoterms_dict = dict()
max_variant_length = 0 # No. of words in longest variant
with open(sys.argv[1] + HPOTERMS_DICT_FILENAME, 'rt') as hpoterms_dict_file:
    for line in hpoterms_dict_file:
        tokens = line.strip().split("\t")
        # 1st token is name, 2nd is description, 3rd and 4th unknown 
        # TODO (Matteo) ask Amir
        name = tokens[0]
        description = tokens[1]
        description_words = description.split()
        variants = get_variants(description_words)
        for variant in variants:
            if len(variant.split()) > max_variant_length:
                max_variant_length = len(variant.split())
            hpoterms_dict[variant.lower()] = name


# Process input
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

    history = set()
    for start in range(len(words)):
        for end in reversed(range(start + 1, min(len(words), start +
            max_variant_length + 1))):

            if start in history or end in history:
                continue
            
            phrase = " ".join(words[start:end])
            phrase_lower = phrase.lower()

            # Very simple rule: if the word is in the dictionary, then is a mention
            if phrase_lower in hpoterms_dict:
                provenance = [ doc_id, sent_id, start, end - 1, phrase ]
                mention_id = "_".join(str(x) for x in (doc_id, sent_id, start, end -1))
                name = hpoterms_dict[phrase_lower]
                print(json.dumps({"id": None, "mention_id": mention_id,
                    "provenance": provenance, "name": name, "is_correct":
                    True}))
                # Found a mention with this start and end: we can insert the
                # indexes of this mention in the history, and break the loop on
                # end and get to a new start
                for i in range(start, end + 1):
                    history.add(i)
                break

