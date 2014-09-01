#! /usr/bin/env python3
#
# Look for acronyms defined in the sentence that look like gene symbols

import json

from helper.dictionaries import load_dict
from helper.easierlife import get_input_sentences

# Yield acronyms from sentence
def extract(sentence):
    # First method: Look for a sentence that starts with "Abbreviations"
    if len(sentence.words) > 0 and sentence.words[0].word == "Abbreviations":
        index = 2
        while index < len(sentence.words):
            acronym = dict()
            acronym["acronym"] = sentence.words[index].word
            try:
                definition_end = sentence.words.index(";", index + 1)
            except:
                definition_end = len(sentence.words) - 1
            # Skip acronym if it's not in the genes dictionary
            if sentence.words[index].word.casefold() not in merged_genes_dict:
                index = definition_end + 1
                continue
            acronym["doc_id"] = sentence.doc_id
            acronym["sent_id"] = sentence.sent_id
            acronym["word_idx"] = sentence.words[index].in_sent_idx
            acronym["definition"] = " ".join([x.word for x in
                sentence.words[index + 1:definition_end]])
            yield acronym
            index = definition_end + 1
    else: 
        # Second method: find 'A Better Example (ABE)' type of definitions.
        # Scan all the words in the sentence
        for word in sentence.words:
            if word.casefold() not in merged_genes_dict:
                continue
            acronym = None
            # Look for definition only if this word has length at least 2 and is
            # all capitals and it comes between "(" and ")" or "(" and ";" or "("
            # and ","
            if word.word.isalpha() and len(word.word) >= 2 and word.word.isupper() \
            and word.in_sent_idx > 0 and word.in_sent_idx < len(sentence.words) - 1 \
            and sentence.words[word.in_sent_idx - 1].word == "(" \
            and sentence.words[word.in_sent_idx + 1].word in [")", ";" ","]:
                word_idx = word.in_sent_idx
                window_size = len(word.word)
                # Look for a sequence of words coming before this one whose
                # initials would create this acronym
                start_idx = 0
                while start_idx + window_size - 1 < word_idx:
                    window_words = sentence.words[start_idx:(start_idx + window_size)]
                    is_definition = True
                    for window_index in range(window_size):
                        if window_words[window_index].word[0].lower() != word.word[window_index].lower():
                            is_definition = False
                            break
                    if is_definition:
                        acronym = dict()
                        acronym["doc_id"] = word.doc_id
                        acronym["sent_id"] = word.sent_id
                        acronym["word_idx"] = word.in_sent_idx
                        acronym["acronym"] = word.word
                        acronym["definition"] = " ".join([w.word for w in window_words])
                        yield acronym
                        break
                    start_idx += 1

# Load the genes dictionary
merged_genes_dict = load_dict("merged_genes")

# Process the input
for sentence in get_input_sentences():
    for acronym in extract(sentence):
        if acronym:
            print(json.dumps(acronym))

