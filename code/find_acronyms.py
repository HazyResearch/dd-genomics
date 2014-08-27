#! /usr/bin/env python3
#
# Look for acronyms defined in the sentence, where an acronym is an upper-case
# word and is defined if the sentence contains a sequence of words that start
# with letters composing the acronym.
#

import json

from helper.easierlife import get_input_sentences

# Yield acronyms from sentence
def extract(sentence):
    # Scan all the words in the sentence
    for word in sentence.words:
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

# Process the input
for sentence in get_input_sentences():
    for acronym in extract(sentence):
        if acronym:
            print(json.dumps(acronym))

