#! /usr/bin/env python3
#
# Takes one or more parser output files in input and emits TSV lines that can
# be loaded # in the 'sentences' table using the PostgreSQL COPY FROM command.
# 
# Parser output files contain "blocks" which are separated by blank lines. Each
# "block"  is a sentence. Each sentence spans over one or more lines. Each line
# represents a # "word" in the sentence (it can be punctuation, a symbol or
# anything). Each word line has *nine* fields:
# 1: index of the word in the sentence, starting from 1.
# 2: the text of the word as it appears in the document
# 3: Part of Speech (POS) tag of the word (see
#    http://www.computing.dcu.ie/~acahill/tagset.html for a list)
# 4: Named Entity Recognition (NER) tag of the word
# 5: the lemmatized word
# 6: the label on the edge in dependency path between the parent of this word
#    and the word
# 7: the word index of the *parent* of this word in the dependency path. 0
#    means root
# 8: the sentence ID, unique in the document
# 9: the bounding box containing this word in the PDF document. The format is
#    "[pXXXlXXXtXXXrXXXbXXX]," for page, left, top, right, bottom
# An example line is:
# 1	Genome	NNP	O	Genome	nn	3	SENT_1	[p1l1669t172r1943b234],
#
# This script outputs TSV lines, one line per sentence. Each line has nine
# columns. The text in the columns is formatted so that the output can be given
# in input to the PostgreSQL 'COPY FROM' command. The columns are the following
# (between parentheses is the PostgreSQL type for the column):
# 1: document ID (text)
# 2: sentence ID (int)
# 3: word indexes (int[]). They now start from 0, like an array.
# 4: words, (text[])
# 5: POSes (text[])
# 6: NERs (text[])
# 7: dependency paths (text[])
# 8: dependency parent (int[]) -1 means root, so that each of them is an array index
# 9: bounding boxes (text[])
#
# Author: Matteo Riondato <rionda@cs.stanford.edu>
#

import os.path
import sys

# Convert a list to a string that can be used in a TSV column and intepreted as
# an array by the PostreSQL COPY FROM command.
# If 'quote' is True, then double quote the string representation of the
# elements of the list, and escape double quotes and backslashes.
def list2TSVarray(a_list, quote=False):
    if quote:
        for index in range(len(a_list)):
            if "\\" in str(a_list[index]):
                # Replace '\' with '\\\\"' to be accepted by COPY FROM
                a_list[index] = str(a_list[index]).replace("\\", "\\\\\\\\")
            # This must happen the previous substitution
            if "\"" in str(a_list[index]):
                # Replace '"' with '\\"' to be accepted by COPY FROM
                a_list[index] = str(a_list[index]).replace("\"", "\\\\\"")
        string = ",".join(list(map(lambda x: "\"" + str(x) + "\"", a_list)))
    else:
        string = ",".join(list(map(lambda x: str(x), a_list)))
    return "{" + string + "}"


# Process the input files
def main():
    script_name = os.path.basename(__file__)
    # Check
    if len(sys.argv) == 1:
        print("USAGE: {} FILE1 [FILE2 [...]]".format(script_name))
        return 1

    # Check that the input files exist
    for filename in sys.argv[1:]:
        if not os.path.exists(filename):
            sys.stderr.write("script_name: ERROR: file '{}' does not exist\n".format(filename))
            return 1

    for filename in sys.argv[1:]:
        # Docid assumed to be the filename.
        docid = os.path.basename(filename)
        with open(filename, 'rt') as curr_file:
            atEOF = False
            # One iteration of the following loop corresponds to one sentence
            while not atEOF: 
                sent_id = -1
                wordidxs = []
                words = []
                poses = []
                ners = []
                lemmas = []
                dep_paths = []
                dep_parents = []
                bounding_boxes = []
                curr_line = curr_file.readline().strip()
                # Sentences are separated by empty lines in the parser output file
                while curr_line != "":
                    tokens = curr_line.split("\t")
                    if len(tokens) != 9:
                        sys.stderr.write("{}: ERROR: malformed line (wrong number of fields): {}\n".format(script_name, curr_line))
                        return 1

                    word_idx, word, pos, ner, lemma, dep_path, dep_parent, word_sent_id, bounding_box = tokens 

                    # Normalize sentence id
                    word_sent_id = int(word_sent_id.replace("SENT_", ""))

                    # assign sentence id if this is the first word of the sentence
                    if sent_id == -1:
                        sent_id = word_sent_id
                    # sanity check for word_sent_id
                    elif sent_id != word_sent_id:
                        sys.stderr.write("{}: ERROR: found word with mismatching sent_id w.r.t. sentence: {} != {}\n".format(script_name, word_sent_id, sent_id))
                        return 1

                    # Normalize bounding box, stripping initial '[' and final '],'
                    bounding_box = bounding_box[1:-2]

                    # Append contents of this line to the sentence arrays
                    wordidxs.append(int(word_idx) - 1) # Start from 0
                    words.append(word) 
                    poses.append(pos)
                    ners.append(ner)
                    lemmas.append(lemma)
                    dep_paths.append(dep_path)
                    # Now "-1" means root and the rest correspond to array indices
                    dep_parents.append(int(dep_parent) - 1) 
                    bounding_boxes.append(bounding_box)

                    # Read the next line
                    curr_line = curr_file.readline().strip()

                # Write sentence to output
                print("\t".join([docid, str(sent_id), list2TSVarray(wordidxs),
                    list2TSVarray(words, quote=True),
                    list2TSVarray(poses, quote=True),
                    list2TSVarray(ners),
                    list2TSVarray(lemmas, quote=True),
                    list2TSVarray(dep_paths, quote=True),
                    list2TSVarray(dep_parents),
                    list2TSVarray(bounding_boxes)]))

                # Check if we are at End of File
                curr_pos = curr_file.tell()
                curr_file.read(1)
                new_pos = curr_file.tell()
                if new_pos == curr_pos:
                    atEOF = True
                else:
                    curr_file.seek(curr_pos)
    return 0


if __name__ == "__main__":
    sys.exit(main())

