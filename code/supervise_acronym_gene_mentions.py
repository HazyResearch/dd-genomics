#! /usr/bin/env python3
#
# Set the is_correct field to false for any input sentence

import fileinput
import json

# Process the input
with fileinput.input() as input_files:
    for line in input_files:
        mention = json.loads(line)
        mention["is_correct"] = False
        print(json.dumps(mention))

