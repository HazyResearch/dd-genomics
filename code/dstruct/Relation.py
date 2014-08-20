#! /usr/bin/env python3
""" A Relation class

Originally obtained from the 'pharm' repository (called 'RelationMention'), but modified.
"""

import json

class Relation(object):

    id = None	
    type = None
    mention_1 = None
    mention_2 = None
    features = None
    is_correct = None
	
    def add_features(self, features):
        for f in features:
            self.features.append(f)

    def __init__(self, _type, _mention_1, _mention_2):
        self.type = _type
        self.features = []
        self.mention_1 = _mention_1
        self.mention_2 = _mention_2

    def dump(self):
        return json.dumps({"id": None, "type":self.type,
            "mention_1":self.mention_1.id, "mention_2":self.mention_2.id,
            "is_correct":self.is_correct, "features":self.features})

    def __repr__(self):
        return "[" + self.type + " : " + self.mention_1.__repr__() + " | " + self.mention_2.__repr__() + "]"

