#! /usr/bin/env python3
""" A generic Mention class 

Originally obtained from the 'pharm' repository, but modified.
"""

import json
from helper.easierlife import serialize

class Mention(object):

    doc_id = None
    sent_id = None
    id = None	
    type = None
    prov_words = None
    features = None
    is_correct = None
    start_word_id = None
    end_word_id = None

    def add_features(self, features):
        """ Add features to the list of features """
	    
        for f in features:
            self.features.append(f)

    def __init__(self, _doc_id, _type, _words):
        self.doc_id = _doc_id
        self.type = _type
        self.prov_words = []
        for w in _words:
            self.prov_words.append(w)
        self.sent_id = _words[0].sent_id
        self.start_word_id = self.prov_words[0].in_sent_idx
        self.end_word_id = self.prov_words[-1].in_sent_idx
        self.id = "MENTION_{}_{}_SENT{}_{}_{}".format(self.type, self.doc_id,
                self.sent_id, self.start_word_id, self.end_word_id)
        self.features = []

    def dump(self, mode="tsv"):
        serialized_obj = serialize(self)

        # XXX There seem to be encoding errors with the features, maybe from OCR?
        # We only use the features that don't have encoding errors.
        # XXX (Matteo) Commented out the encoding. 
        valid_features = []
        for feature in self.features:
            valid_features.append("'" + feature.replace("'", '_').replace('{', '-_-').replace('}','-__-').replace('"', '-___-') + "'")
            #try:
            #    valid_features.append("'" + feature.encode("ascii", "ignore").replace("'", '_').replace('{', '-_-').replace('}','-__-').replace('"', '-___-') + "'")
            #except:
            #    continue

        if mode == "tsv":
            ict = "\\N"
            if self.is_correct != None:
                ict = self.is_correct.__repr__()
            return "\t".join(["\\N", self.doc_id, self.sent_id.__repr__(),
                self.id, self.start_word_id.__repr__(),
                self.end_word_id.__repr__(), self.type, ict,
                self.__repr__().encode("ascii", "ignore"), '{' +
                ",".join(valid_features) + '}', serialized_obj])
        elif mode == "json":
            js_obj = {"doc_id":self.doc_id, "mention_id":self.id, "type":self.type,
        	"repr": self.__repr__(), "is_correct":self.is_correct,
        	"features": valid_features, "sent_id":self.sent_id, "start_word_id":self.start_word_id,
        	"end_word_id":self.end_word_id, "object":serialized_obj}
            return json.dumps(js_obj)
        else:
            return None

    def __repr__(self):
        return "[" + self.type + " : " + " ".join([w.word for w in self.prov_words]) + "]"

