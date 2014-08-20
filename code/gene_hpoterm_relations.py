#! /usr/bin/env python3

import fileinput
import json
from dstruct.Sentence import Sentence
from extractor.RelationExtractor_GeneHPOterm import RelationExtractor_GeneHPOterm
from helper.easierlife import deserialize

extractor = RelationExtractor_GeneHPOterm()

for line in fileinput.input():
    row = json.loads(line)
    gene_mention = deserialize(row["gene"])
    hpoterm_mention = deserialize(row["hpoterm"])
    sentence = Sentence(row["doc_id"], row["sent_id"], row["wordidxs"],
            row["words"], row["poses"], row["ners"], row["lemmas"],
            row["dep_paths"], row["dep_parents"], row["bounding_boxes"])

    # Extract the relation mention
    relation = extractor.extract(sentence, gene_mention, hpoterm_mention)
    print(relation.dump())

