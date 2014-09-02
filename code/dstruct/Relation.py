#! /usr/bin/env python3
""" An object representing a relation

"""

import json

from helper.easierlife import list2TSVarray

class Relation(object):
    doc_id = None
    sent_id = None
    id = None
    type = None
    mention_1_words = None
    mention_2_words = None
    features = None
    is_correct = None

    def __init__(self, _type, mention_1_words, mention_2_words):
        self.doc_id = mention_1_words[0].doc_id
        self.sent_id = mention_1_words[1].sent_id
        self.type = _type
        self.id = "RELATION_{}_{}_{}_{},{}_{},{}".format(self.type,
                self.doc_id, self.sent_id, mention_1_words[0].in_sent_idx,
                mention_1_words[-1].in_sent_idx, mention_2_words[0].in_sent_idx,
                mention_2_words[-1].in_sent_idx)
        self.mention_1_words = mention_1_words
        self.mention_2_words = mention_2_words
        self.features = []

    def add_feature(self, feature):
        self.features.append(feature)

    def add_features(self, features):
        for f in features:
            self.features.append(f)

    def json_dump(self):
        return json.dumps({"id": None, "doc_id": self.doc_id, "sent_id":
            self.sent_id, "relation_id": self.id, "type":self.type,
            "wordidxs_1": [x.in_sent_idx for x in self.mention_1_words],
            "wordidxs_2": [x.in_sent_idx for x in self.mention_2_words],
            "words_1" : [x.word for x  in self.mention_1_words],
            "words_2" : [x.word for x  in self.mention_2_words],
            "is_correct":self.is_correct, "features":self.features})

    def tsv_dump(self):
        is_correct_str = "\\N"
        if self.is_correct != None:
            is_correct_str = self.is_correct.__repr__()
        return "\t".join(self.doc_id, str(self.sent_id), self.id, self.type,
                list2TSVarray([x.in_sent_idx for x in self.mention1_words]),
                list2TSVarray([x.in_sent_idx for x in self.mention2_words]),
                list2TSVarray([x.word for x in self.mention1_words], quote=True),
                list2TSVarray([x.word for x in self.mention2_words], quote=True), 
                is_correct_str, list2TSVarray(self.features, quote=True))

