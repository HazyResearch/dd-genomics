#! /usr/bin/env python3
#
# Take the output of 'find_acronyms.py' and verify which definitions
# corresponds to gene for sure, potentially, or almost surely not. This is then
# used for distant supervision of gene mentions candidates.

import fileinput
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, list2TSVarray, no_op, \
    TSVstring2list

# Load the genes dictionary
merged_genes_dict = load_dict("merged_genes")

if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "acronym", "definitions"],
                [no_op, no_op, TSVstring2list])
            contains_kw = False
            is_correct = None
            for definition in line_dict["definitions"]:
                # If the definition is in the gene dictionary, supervise as
                # correct
                if definition in merged_genes_dict:
                    is_correct = True
                    break
                else:
                    # Check if the definition contains some keywords that
                    # make us suspect that it is probably a gene/protein.
                    # This list is incomplete, and it would be good to add
                    # to it.
                    if contains_kw:
                        continue
                    for word in definition.split():
                        if word.endswith("ase") and len(word) > 5:
                            contains_kw = True
                            break
                    if " gene" in definition or \
                            "protein" in definition or \
                            "factor" in definition or \
                            "ligand" in definition or \
                            "enzyme" in definition or \
                            "receptor" in definition or \
                            "pseudogene" in definition:
                        contains_kw = True
            # If no significant keyword in any definition, supervise as not
            # correct
            if not contains_kw and not is_correct:
                is_correct = False
            is_correct_str = "\\N"
            if is_correct is not None:
                is_correct_str = is_correct.__repr__()
            print("\t".join(
                (line_dict["doc_id"], line_dict["acronym"],
                 list2TSVarray(line_dict["definitions"], quote=True),
                 is_correct_str)))
