#! /usr/bin/env python3
#
# Look for acronyms defined in the sentence that look like gene symbols
#
# This script analyzes one sentence at a time and does not do anything more
# than that. The script 'doc_acronyms.py' will "classify" the acronyms and
# their definitions so they can be used for distant supervision of gene
# mentions candidate.

import fileinput
from dstruct.Sentence import Sentence
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2list


# Return acronyms from sentence
def extract(sentence):
    acronyms = []
    # First method: Look for a sentence that starts with "Abbreviations"
    if len(sentence.words) > 2 and \
            sentence.words[0].word.casefold() == "abbreviations" and \
            (sentence.words[1].word.casefold() == ":" or 
                    sent.words[1].word == "used"):
        words = [x.word for x in sentence.words]
        index = 2
        while index < len(words):
            acronym = dict()
            acronym["acronym"] = words[index]
            # There are a lot of typos and different separators used in the
            # text, this is obviously a best effort ...
            try:
                comma_index = words.index(",", index + 1)
            except:
                comma_index = len(words)
            try:
                semicolon_index = words.index(";", index + 1)
            except:
                semicolon_index = len(words)
            try:
                colon_index = words.index(":", index + 1)
            except:
                colon_index = len(words)
            definition_start = min(
                [comma_index, semicolon_index, colon_index]) + 1
            if definition_start > len(words):
                definition_start = index + 1
            try:
                definition_end = words.index(";", definition_start + 1)
            except:
                if words[-1] == ".":
                    definition_end = len(words) - 1
                else:
                    definition_end = len(words)
            definition = " ".join(words[definition_start:definition_end])
            if words[index] not in merged_genes_dict or \
                    words[index] in inverted_long_names:
                index = definition_end + 1
                continue
            # If we didn't find a definition, give up
            if definition.strip() == "":
                index = definition_end + 1
                continue
            acronym["doc_id"] = sentence.doc_id
            acronym["sent_id"] = sentence.sent_id
            acronym["word_idx"] = sentence.words[index].in_sent_idx
            acronym["definition"] = definition
            acronyms.append(acronym)
            index = definition_end + 1
    else:
        # Second method: find 'A Better Example (ABE)' type of definitions.
        # Skip first and last word of sentence, to allow for "(" and ")".
        for word in sentence.words[1:-1]:
            acronym = None
            # Look for definition only if 
            # - this word is in the genes dictionary AND
            # - is uppercase AND
            # - it only contains letters AND
            # - it has length at least 2  AND
            # - it comes between "(" and ")" or "(" and ";" # or "(" # and "," 
            if word.word in merged_genes_dict and \
                    word.word not in inverted_long_names and \
                    word.word.isupper() and word.word.isalpha() and \
                    len(word.word) >= 2 and \
                    ((sentence.words[word.in_sent_idx - 1].word == "(" and
                      sentence.words[word.in_sent_idx + 1].word in [
                      ")", ";" ",", "]"]) or
                     (sentence.words[word.in_sent_idx - 1].word == "[" and
                      sentence.words[word.in_sent_idx + 1].word == "]")):
                word_idx = word.in_sent_idx
                window_size = len(word.word)
                # Look for a sequence of words coming before this one whose
                # initials would create this acronym
                start_idx = 0
                while start_idx + window_size - 1 < word_idx:
                    window_words = sentence.words[start_idx:(start_idx +
                                                             window_size)]
                    is_definition = True
                    for window_index in range(window_size):
                        if window_words[window_index].word[0].lower() != \
                                word.word[window_index].lower():
                            is_definition = False
                            break
                    definition = " ".join([w.word for w in window_words])
                    # Only consider this acronym if the definition is valid
                    if is_definition:
                        acronym = dict()
                        acronym["doc_id"] = word.doc_id
                        acronym["sent_id"] = word.sent_id
                        acronym["word_idx"] = word.in_sent_idx
                        acronym["acronym"] = word.word
                        acronym["definition"] = definition
                        acronyms.append(acronym)
                        break
                    start_idx += 1
    return acronyms


# Load the genes dictionary
merged_genes_dict = load_dict("merged_genes")
inverted_long_names = load_dict("inverted_long_names")

if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line,
                ["doc_id", "sent_id", "wordidxs", "words", "poses", "ners",
                    "lemmas", "dep_paths", "dep_parents",
                    "bounding_boxes"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list])
            # Create the Sentence object
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Extract the acronyms and print them
            for acronym in extract(sentence):
                print("\t".join([acronym["doc_id"], str(acronym["sent_id"]),
                                 str(acronym["word_idx"]), acronym["acronym"],
                                 acronym["definition"]]))
