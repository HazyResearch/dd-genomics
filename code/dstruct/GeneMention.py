#! /usr/bin/env python3
""" A mention class for genes mentions """

from dstruct.Mention import *

class GeneMention(Mention):
    symbol = None
    TYPE = "GENE"

    def __init__(self, _docid, _symbol, _words):
        super(GeneMention, self).__init__(_docid, TYPE, _words)
        self.symbol = _symbol

