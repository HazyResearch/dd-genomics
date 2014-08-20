#! /usr/bin/env python3

from Extractor import RelationExtractor
from dstruct.RelationMention import RelationMention

class RelationExtractor_GeneHPOterm(RelationExtractor):
    def __init__(self):
        pass

    def supervise(self, sentence, gene, hpoterm, rel):
        pass

    def extract(self, sentence, gene, hpoterm):
        rel = RelationMention("GENEHPOTERM", gene, hpoterm)

        self.supervise(sentence, gene, hpoterm, rel)

        # Add features
        # 
        rel.add_features([sentence.dep_path(gene, hpoterm),])

        return rel

