#! /usr/bin/env python3
#
# Extract, add features to, and supervise mentions extracted from geneRifs.
#

import fileinput
import sys

from dstruct.Sentence import Sentence
from extract_gene_mentions import extract, add_features
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op
from helper.dictionaries import load_dict


def main():
    # Load the merged genes dictionary
    merged_genes_dict = load_dict("merged_genes")
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
            # Get the main symbol (or list of symbols) for the gene
            if gene in merged_genes_dict:
                gene = merged_genes_dict[gene]
            else:
                gene = [gene, ]
            # Skip sentences that are "( GENE )"
            if (sentence.words[0].word == "-LRB-" and
                    sentence.words[-1].word == "-RRB-") or \
               (sentence.words[0].word == "-LSB-" and
                    sentence.words[-1].word == "-RSB-"):
                        continue
            # Extract mentions from sentence
            mentions = extract(sentence)
            # Check whether this mention contains the 'labelled' gene
            # If so, supervise positively and print
            found_main = False
            not_main_mentions = []
            for mention in mentions:
                mention.type = "GENERIFS"
                add_features(mention, sentence)
                if "NOT_ENGLISH_WORDS_IN_SENTENCE" not in mention.features:
                    for g in gene:
                        if not found_main and \
                                mention.words[0].word.find(g) > -1:
                            found_main = True
                            mention.is_correct = True
                            print(mention.tsv_dump())
                        if not found_main and mention.entity.find(g) > -1:
                            mention.is_correct = True
                            not_main_mentions.append(mention)
            if not found_main:
                for mention in not_main_mentions:
                    print(mention.tsv_dump())
    return 0

if __name__ == "__main__":
    sys.exit(main())
