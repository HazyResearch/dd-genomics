#! /usr/bin/env python3
""" A Word class

Originally obtained from the 'pharm' repository, but modified.
"""

class Word(object):
  
    insent_idx = None
    word = None
    pos = None
    ner = None
    lemma = None
    dep_path = None
    dep_parent = None
    sent_id = None
    box = None

    def __init__(self, _sent_id, _in_sent_idx, _word, _pos, _ner, _lemma, _dep_path, _dep_parent, _box):
        self.sent_id = _sent_id
        # We subtract 1 so it starts from 0 (the parser output files have it
        # starting from 1). This allows us to use _in_sent_idx as index in the
        # Sentence.words array.
        # XXX (Matteo) Should this be done in the parser2sentences.py script?
        self.in_sent_idx = _in_sent_idx - 1 
        self.word = _word
        self.pos = _pos
        self.ner = _ner
        # As before for in_sent_idx. This allows us to follow dependency paths.
        # Note that the value -1 now denotes the root.
        self.dep_parent = _dep_parent - 1 
        self.dep_path = _dep_path
        self.box = _box
        self.lemma = _lemma
        # If do not do the following, outputting an Array in the language will crash
        # XXX (Matteo) This was in the original code, not sure what it means
        self.lemma = self.lemma.replace('"', "''") 
        self.lemma = self.lemma.replace('\\', "_") 

    def __repr__(self):
        return self.word

    # Return the NER tag if different than 'O', otherwise return the lemma
    def get_feature(self):
        if self.ner == 'O':
            return self.lemma
        else:
            return self.ner

