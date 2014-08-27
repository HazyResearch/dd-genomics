#! /usr/bin/env python3
""" An object representing a relation

"""

import json

class Relation(object):
    doc_id = None
    sent_id = None
    id = None
    type = None
    mention_words_1 = None
    mention_words_2 = None
    wordidxs = None
    features = None
    is_correct = None

    def add_feature(self, feature):
        self.features.append(feature)
	
    def add_features(self, features):
        for f in features:
            self.features.append(f)

    def __init__(self, _type, sentence, mention_1_start_word_idx,
            mention_1_end_word_idx, mention_2_start_word_idx,
            mention_2_end_word_idx):
        self.doc_id = sentence.doc_id
        self.sent_id = sentence.sent_id
        self.type = _type
        self.id = "RELATION_{}_{}_{}_{},{}_{},{}".format(self.type,
                self.doc_id, self.sent_id, mention_1_start_word_idx,
                mention_1_end_word_idx, mention_2_start_word_idx,
                mention_2_end_word_idx)
        self.wordidxs = [x for x in range(mention_1_start_word_idx,
            mention_1_end_word_idx + 1)] + [x for x in
                    range(mention_2_start_word_idx, mention_2_end_word_idx +
                        1)]
        self.mention_1_words
        self.features = []

    def json_dump(self):
        return json.dumps({"id": None, "type":self.type,
            "mention_1":self.mention_1.id, "mention_2":self.mention_2.id,
            "is_correct":self.is_correct, "features":self.features})

    def __repr__(self):
        return "[" + self.type + " : " + self.mention_1.__repr__() + " | " + self.mention_2.__repr__() + "]"

