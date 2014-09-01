#! /usr/bin/env python3
#
# Extract, add features to, and supervise mentions extracted from geneRifs.
# Print a big warning if we don't find a mention contained the labelled gene.
#

import fileinput
import json
import sys

from dstruct.Sentence import Sentence
from extract_gene_mentions import extract, add_features

def main():
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            line_dict = json.loads(line)
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
                add_features(mention)
                # Check whether this mention contains the 'labelled' gene
                # XXX (Matteo) is this the right check?
                if mention.entity.find(gene) > -1: 
                    found_gene = True
                    mention.is_correct = True
                print(mention.json_dump())
            # Print big warning if we did not find the 'labelled' gene
            # and exit with failure code!
            if not found_gene:
                sys.stderr.err("WARNING: Not found mention of '{}' in geneRifs {} ('{}')\n".format(gene, line_dict["doc_id"], " ".join(line_dict["words"])))
                return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

