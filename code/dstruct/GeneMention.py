#! /usr/bin/env python3
""" A mention class for genes mentions """

from dstruct.Mention import *

class GeneMention(Mention):
    symbol = None
    TYPE = "GENE"

    def __init__(self, _doc_id, _symbol, _words):
        super(GeneMention, self).__init__(_doc_id, TYPE, _words)
        self.symbol = _symbol

