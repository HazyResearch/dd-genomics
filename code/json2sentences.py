#! /usr/bin/env python3
#

import fileinput
import json
import sys

from parser2sentences import list2TSVarray


if len(sys.argv) < 2:
    sys.stderr.write("USAGE: {} FILE [FILE [FILE [...]]]\n".format(sys.argv[0]))
    sys.exit(1)

with fileinput.input() as input_files:
    for line in input_files:
        line_dict = json.loads(line)
        docid = line_dict["doc_id"]
        sent_id = line_dict["sent_id"]
        words = line_dict["words"]
        wordidxs = [x for x in range(len(words))]
        poses = line_dict["poses"]
        ners = line_dict["ners"]
        lemmas = line_dict["lemmas"]
        dep_paths = line_dict["dep_paths"]
        dep_parents = line_dict["dep_parents"]
        bounding_boxes = []

        print("{}\n".format("\t".join([docid, str(sent_id),
            list2TSVarray(wordidxs), list2TSVarray(words,
                quote=True), list2TSVarray(poses, quote=True),
            list2TSVarray(ners), list2TSVarray(lemmas, quote=True),
            list2TSVarray(dep_paths, quote=True),
            list2TSVarray(dep_parents),
            list2TSVarray(bounding_boxes)])))

