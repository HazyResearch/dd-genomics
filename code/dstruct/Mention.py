#! /usr/bin/env python3
""" A generic Mention class 

Originally obtained from the 'pharm' repository, but modified.
"""

from helper.easierlife import *

class Mention(object):

    docid = None
    sentid = None
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

    def __init__(self, _docid, _type, _words):
        self.docid = _docid
        self.type = _type
        self.prov_words = []
        for w in _words:
            self.prov_words.append(w)
        self.sentid = _words[0].sentid
        self.start_word_id = self.prov_words[0].insent_id
        self.end_word_id = self.prov_words[-1].insent_id
        self.id = "MENTION_%s_%s_SENT%d_%d_%d" % (self.type, self.docid, self.sentid, self.start_word_id, self.end_word_id)
        self.features = []

    def dumps(self, mode="tsv"):
        # TODO (Matteo) Ask Ce why one would need the following.
        #serialized_obj = serialize(self)

        # XXX There seem to be encoding errors with the features, maybe from OCR?
        # We only use the features that don't have encoding errors.
        valid_features = []
        for feature in self.features:
            try:
                valid_features.append("'" + feature.encode("ascii", "ignore").replace("'", '_').replace('{', '-_-').replace('}','-__-').replace('"', '-___-') + "'")
            except:
                continue

        if mode == "tsv":
            ict = "\\N"
            if self.is_correct != None:
                ict = self.is_correct.__repr__()
            return "\t".join(["\\N", self.docid, self.sentid.__repr__(), self.id, self.start_word_id.__repr__(), self.end_word_id.__repr__(), self.type, ict, self.__repr__().encode("ascii", "ignore"), '{' + ",".join(valid_features) + '}', serialized_obj])
        elif mode == "json":
            js_obj = {"docid":self.docid, "mentionid":self.id, "type":self.type,
        	"repr":self.__repr__().decode("utf-8"), "is_correct":self.is_correct,
        	"features": valid_features, "sentid":self.sentid, "start_word_id":self.start_word_id,
        	"end_word_id":self.end_word_id}
                # TODO (Matteo) Commenting out until we find out why we would
                # need it
        	#"object":serialized_obj}
            return json.dumps(js_obj)
        else:
            return None

    def __repr__(self):
        return "[" + self.type + " : " + " ".join([w.word for w in self.prov_words]) + "]"

