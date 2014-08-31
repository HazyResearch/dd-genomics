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
        dep_paths_orig = line_dict["dep_paths"]
        bounding_boxes = [""] * len(words)

        dep_paths = ["_"] * len(words)
        dep_parents = [0] * len(words)
        assert len(words) == len(poses)
        assert len(words) == len(ners)
        assert len(words) == len(lemmas)
        for dep_path in dep_paths_orig:
            tokens = dep_path.split("(")
            dep_parent = int((tokens[1].split(",")[0]).split("-")[1]) - 1
            dep_child = int((tokens[1].split(",")[1]).split("-")[1][:-1]) - 1
            dep_paths[dep_child] = tokens[0]
            dep_parents[dep_child] = dep_parent

        print("{}\n".format("\t".join([docid, str(sent_id),
            list2TSVarray(wordidxs), list2TSVarray(words,
                quote=True), list2TSVarray(poses, quote=True),
            list2TSVarray(ners), list2TSVarray(lemmas, quote=True),
            list2TSVarray(dep_paths, quote=True),
            list2TSVarray(dep_parents),
            list2TSVarray(bounding_boxes)])))

