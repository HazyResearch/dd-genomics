#! /usr/bin/env python3
""" A generic Mention class 

Originally obtained from the 'pharm' repository, but modified.
"""

import json

class Mention(object):

    doc_id = None
    sent_id = None
    start_word_idx = None
    end_word_idx = None
    id = None	
    type = None
    entity = None
    words = None
    features = None
    is_correct = None

    def __init__(self, _type, _entity, _words):
        self.doc_id = _words[0]._doc_id
        self.sent_id = _words[0].sent_id
        self.start_word_idx = _words[0].in_sent_idx
        self.end_word_idx = _words[-1].in_sent_idx
        self.id = "MENTION_{}_{}_{}_{}_{}".format(self.type, self.doc_id,
                self.sent_id, self.start_word_idx, self.end_word_idx)
        self.type = _type
        self.entity = _entity;
        # These are Word objects
        self.words = []
        for w in _words:
            self.words.append(w)
        self.features = []
        self.is_correct = None

    def __repr__(self):
        return " ".join([w.word for w in self.words])

    ## Dump self to a json object
    def json_dump(self):
        json_obj = {"doc_id": self.doc_id, "sent_id": self.sent_id,
                "start_word_idx": self.start_word_idx,
                "end_word_idx": self.end_word_idx, 
                "mention_id": self.id, "type": self.type,
                "entity": self.entity,
                "words": [w.word for w in self.words],
                "is_correct":self.is_correct,
                "features": self.features}
        return json.dumps(json_obj)


    ## Add a feature
    def add_feature(self, feature):
        self.features.append(feature)

    ## Add multiple features
    def add_features(self, features):
        for feature in features:
            self.add_feature(feature)

