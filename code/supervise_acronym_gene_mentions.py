#! /usr/bin/env pyton3

import fileinput
import json

# Process the input
with fileinput.input() as input_files:
    for line in input_files:
        mention = json.loads(line)
        mention.is_correct = False
        print(json.dumps(mention))

