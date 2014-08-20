#! /usr/bin/env python3
""" A mention class for HPO terms mentions """

from dstruct.Mention import Mention

class HPOtermMention(Mention):
    term = None

    def __init__(self, _doc_id, _term, _words):
        super(HPOtermMention, self).__init__(_doc_id, "HPOTERM", _words)
        self.term = _term

