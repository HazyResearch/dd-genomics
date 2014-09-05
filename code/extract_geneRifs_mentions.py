#! /usr/bin/env python3
#
# Extract, add features to, and supervise mentions extracted from geneRifs.
#

import fileinput
import sys

from dstruct.Sentence import Sentence
from extract_gene_mentions import extract, add_features, add_features_to_all
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op


def main():
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "bounding_boxes", "gene"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list, no_op])
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # This is the 'labelled' gene that we know is in the sentence
            gene = line_dict["gene"]
            # Extract mentions from sentence
            mentions = extract(sentence)
            if len(mentions) > 1:
                add_features_to_all(mentions, sentence)
                # Check whether this mention contains the 'labelled' gene
                # If so, supervise positively and print
            for mention in mentions:
                add_features(mention, sentence)
                if mention.entity.find(gene) > -1 or \
                        mention.words[0].word.find(gene) > -1:
                    mention.is_correct = True
                    print(mention.tsv_dump())
    return 0

if __name__ == "__main__":
    sys.exit(main())
