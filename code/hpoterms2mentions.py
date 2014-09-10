#! /usr/bin/env python3
#
# Map phenotype entities to mentions

import sys
from nltk.stem.snowball import SnowballStemmer

from helper.dictionaries import load_dict


def main():
	# Load the dictionaries we need
    stopwords_dict = load_dict("stopwords")
    hpodag_dict = load_dict("hpodag")
    # Load the stemmer from NLTK
    stemmer = SnowballStemmer("english")
    if len(sys.argv) != 2:
        sys.stderr.write("USAGE: {} DICT\n".format(sys.argv[0]))
        sys.exit(1)
    with open(sys.argv[1], 'rt') as dict_file:
        for line in dict_file:
			# Skip empty lines
            if line.strip() == "":
                continue
            hpo_id, name, definition = line.strip().split("\t")
            # Skip if this is not a phenotypic abnormality
            try:
                if "HP:0000118" not in hpodag_dict[hpo_id]:
                    continue
            except:  # skip terms with no ancestors in the dag, e.g., HP:0000489
                continue 
			# Compute the stems of the name
            name_stems = set()
            for word in name.split():
				# Remove parenthesis and commas
                if word[0] == "(":
                    word = word[1:]
                if word[-1] == ")":
                    word = word[:-1]
                if word[-1] == ",":
                    word = word[:-1]
                # Only process non stop-words AND single letters
                if word.casefold() not in stopwords_dict or len(word) == 1:
					# split words that contain a "/"
                    if word.find("/") != - 1:
                        for part in word.split("/"):
                            name_stems.add(stemmer.stem(part))
                    else:
                        name_stems.add(stemmer.stem(word))
            print("\t".join([hpo_id, name, "|".join(name_stems)]))


if __name__ == "__main__":
    sys.exit(main())
