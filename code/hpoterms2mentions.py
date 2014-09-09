#! /usr/bin/env python3
#
# Map phenotype entities to mentions

import sys
from nltk.stem.snowball import SnowballStemmer

from helper.dictionaries import load_dict


def main():
    stopwords_dict = load_dict("stopwords")
    stemmer = SnowballStemmer("english")
    if len(sys.argv) != 2:
        sys.stderr.write("USAGE: {} DICT\n".format(sys.argv[0]))
        sys.exit(1)
    with open(sys.argv[1], 'rt') as dict_file:
        for line in dict_file:
            if line.strip() == "":
                continue
            hpo_id, name, definition = line.strip().split("\t")
            name_stems = set()
            for word in name.split():
                if word[0] == "(":
                    word = word[1:]
                if word[-1] == ")":
                    word = word[:-1]
                if word[-1] == ",":
                    word = word[:-1]
                if word.casefold() not in stopwords_dict or len(word) == 1:
                    if word.find("/") != - 1:
                        for part in word.split("/"):
                            name_stems.add(stemmer.stem(part))
                    else:
                        name_stems.add(stemmer.stem(word))
            print("\t".join([hpo_id, name, "|".join(name_stems)]))


if __name__ == "__main__":
    sys.exit(main())
