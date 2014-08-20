#! /usr/bin/env python3

import re
from Extractor import RelationExtractor
from dstruct.RelationMention import RelationMention

class RelationExtractor_GeneHPOterm(RelationExtractor):
    def __init__(self):
        pass

    # Perform the distant supervision
    # TODO (Matteo) implement
    def supervise(self, sentence, gene, hpoterm, rel):
        pass

    # Extract the relation mentions
    def extract(self, sentence, gene, hpoterm):
        relation = RelationMention("GENEHPOTERM", gene, hpoterm)

        self.supervise(sentence, gene, hpoterm, relation)

        # Add features
        gene_start = int(gene.id.split("_")[4])
        hpoterm_start = int(hpoterm.id.split("_")[4])
        gene_end = int(gene.id.split("_")[5])
        hpoterm_end = int(hpoterm.id.split("_")[5])
        start = min(gene_start, hpoterm_start)
        end = max(gene_end, hpoterm_end)
        sent_words_between = " ".join([w.lemma for w in sentence.words[start:end]])

        # Verb between the two words, if present
        for word in sent_words_between:
                if re.search('VB\w*', word.pos):
                        relation.add_features(["verb="+word.lemma])
        # Word sequence between words
        relation.add_features(["word_seq="+"_".join(sent_words_between)])
        # Left and windows
        if start > 0:
            relation.add_features(["window_left_1={}".format(sentence.words[start-1])])
        if end < len(sentence.words) - 1:
            relation.add_features(["window_right_1={}".format(sentence.words[end])])

        # Shortest dependency path between the two
        gene_symbol = gene.symbol
        hpoterm_term = hpoterm.name.lower()
        relation.add_features([sentence.dep_path(gene_symbol, hpoterm_term),])

        return relation

