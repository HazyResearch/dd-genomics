#! /usr/bin/env python3
#
# Extract, add features to, and supervise mentions extracted from geneRifs.
# Print a big warning if we don't find a mention contained the labelled gene.
#

import fileinput
import sys

from dstruct.Sentence import Sentence
from extract_gene_mentions import extract, add_features
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op

def main():
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # This is for the json case
            #line_dict = json.loads(line)
            # This is for the tsv case
            line_dict = get_dict_from_TSVline(line, ["doc_id", "sent_id", "wordidxs",
            "words", "poses", "ners", "lemmas", "dep_paths", "dep_parents",
            "bounding_boxes", "gene"], [no_op, int, lambda x :
                TSVstring2list(x, int), TSVstring2list, TSVstring2list,
                TSVstring2list, TSVstring2list, TSVstring2list, lambda x :
                TSVstring2list(x, int), TSVstring2list, no_op])
            sentence = Sentence(line_dict["doc_id"], line_dict["sent_id"],
                    line_dict["wordidxs"], line_dict["words"],
                    line_dict["poses"], line_dict["ners"], line_dict["lemmas"],
                    line_dict["dep_paths"], line_dict["dep_parents"],
                    line_dict["bounding_boxes"])
            # This is the 'labelled' gene that we know is in the sentence
            gene = line_dict["gene"]
            found_gene = False
            # Extract mentions from sentence
            for mention in extract(sentence):
                add_features(mention, sentence)
                # Check whether this mention contains the 'labelled' gene
                # Only print it if that is the case
                if mention.entity.find(gene) > -1 or mention.words[0].word.find(gene) > -1: 
                    found_gene = True
                    mention.is_correct = True
                    # this is for json
                    #print(mention.json_dump())
                    # this is for tsv
                    print(mention.tsv_dump())
            # Print big warning if we did not find the 'labelled' gene
            #if not found_gene:
            #    sys.stderr.err("WARNING: Not found mention of '{}' in geneRifs {} ('{}')\n".format(gene, line_dict["doc_id"], " ".join(line_dict["words"])))
    return 0

if __name__ == "__main__":
    sys.exit(main())

