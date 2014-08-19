#! /usr/bin/env python3
""" A mention class for HPO terms mentions """

from dstruct.Mention import *

TYPE = "HPOTERM"

class HPOterm_Mention(Mention):
    term = None

    def __init__(self, _docid, _symbol, _words):
        super(HPOterm_Mention, self).__init__(_docid, TYPE, _words)
        self.symbol = _symbol

