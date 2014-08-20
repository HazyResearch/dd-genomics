#! /usr/bin/env python3
#
import fileinput
import json
from extractor.MentionExtractor_HPOterm import MentionExtractor_HPOterm
from dstruct.Sentence import Sentence

#MODE = "tsv"
MODE = "json"

def TSVarray2list(_list):
    # TODO (Matteo) implement this (should be in helper.easierlife)
    return []

def get_input_sentences(mode="tsv"):
    for line in fileinput.input():
        if mode == "tsv":
            tokens = line.split("\t")
            doc_id = tokens[0]
            sent_id = int(tokens[1])
            words = tokens[2]
            poses = tokens[3]
            ners = tokens[4]
            lemmas = tokens[5]
            dep_paths = tokens[6]
            dep_parents = tokens[7]
            bounding_boxes = tokens[8]
            yield Sentence(doc_id, sent_id, TSVarray2list(words),
                    TSVarray2list(poses), TSVarray2list(ners),
                    TSVarray2list(lemmas), TSVarray2list(dep_paths),
                    TSVarray2list(dep_parents), TSVarray2list(bounding_boxes))

        elif mode == "json":
            sent_dict = json.loads(line)
            yield Sentence(sent_dict["doc_id"], sent_dict["sent_id"],
                    sent_dict["words"], sent_dict["poses"], sent_dict["ners"],
                    sent_dict["lemmas"], sent_dict["dep_paths"],
                    sent_dict["dep_parents"], sent_dict["bounding_boxes"])
        else:
            break

# Initialize the extractor
mention_extractor = MentionExtractor_HPOterm()

for sentence in get_input_sentences(MODE):
    for mention in mention_extractor.extract(sentence):
        if mention != None:
            mention.dump(MODE)
    

