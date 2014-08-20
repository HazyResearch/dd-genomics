#! /usr/bin/env python3
""" Helper functions to make our life easier.

Originally obtained from the 'pharm' repository, but modified.
"""

import fileinput
import json
import zlib
import base64
import sys
import os.path
import pickle


BASE_FOLDER, throwaway = os.path.split(os.path.realpath(__file__))
BASE_FOLDER = BASE_FOLDER + "/../../"


def get_all_phrases_in_sentence(sent, max_phrase_length):
    """ Return the start and end indexes of all subsets of words in the sentence sent,
    with size at most max_phrase_length"""

    for start in range(len(sent.words)):
        for end in reversed(range(start + 1, min(len(sent.words), start + 1 + max_phrase_length))):
            yield (start, end)


def log(str):
    """ Write str to stderr """

    sys.stderr.write(str.__repr__() + "\n")


def asciiCompress(data, level=9):
    """ compress data to printable ascii-code """

    code = zlib.compress(data,level)
    #csum = zlib.crc32(code)
    code = base64.encodestring(code)
    return code.replace('\n', ' ')


def asciiDecompress(code):
    """ decompress result of asciiCompress """

    code = base64.decodestring(code.replace(' ', '\n'))
    #csum = zlib.crc32(code)
    data = zlib.decompress(code)
    return data


def serialize(obj, mode="ascii"):
    """ Return a serialized object with the specified mode """

    if mode == "zlib":
        return zlib.compress(pickle.dumps(obj))
    elif mode == "ascii":
        return asciiCompress(pickle.dumps(obj))
    else:
        return None


def deserialize(obj):
    """ Deserialize an object """
    #return pickle.loads(str(unicode(obj)))
    return pickle.loads(asciiDecompress(obj.encode("utf-8")))


def get_inputs():
    """ Yield dictionaries obtained by parsing each row in input using json """

    for line in fileinput.input():
            yield json.loads(line)


def dump_input(OUTFILE):
    """ Dump the input to a file """

    with open(OUTFILE, 'w') as outfile:
        for line in fileinput.input():
            outfile.write(line)

