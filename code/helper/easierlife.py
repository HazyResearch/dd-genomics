#! /usr/bin/env python3
""" Helper functions to make our life easier.

Originally obtained from the 'pharm' repository, but modified.
"""

import fileinput
import json
import os.path
import sys

from dstruct.Sentence import Sentence

## BASE_DIR denotes the application directory
BASE_DIR, throwaway = os.path.split(os.path.realpath(__file__))
BASE_DIR = os.path.realpath(BASE_DIR + "/../..")


## Return the start and end indexes of all subsets of words in the sentence
## sent, with size at most max_phrase_length
def get_all_phrases_in_sentence(sent, max_phrase_length):
    for start in range(len(sent.words)):
        for end in reversed(range(start + 1, min(len(sent.words), start + 1 + max_phrase_length))):
            yield (start, end)

## Return Sentence objects from input lines
def get_input_sentences(input_files=sys.argv[1:]):
    with fileinput.input(files=input_files) as f:
        for line in f:
            sent_dict = json.loads(line)
            yield Sentence(sent_dict["doc_id"], sent_dict["sent_id"],
                    sent_dict["wordidxs"], sent_dict["words"],
                    sent_dict["poses"], sent_dict["ners"], sent_dict["lemmas"],
                    sent_dict["dep_paths"], sent_dict["dep_parents"],
                    sent_dict["bounding_boxes"])

