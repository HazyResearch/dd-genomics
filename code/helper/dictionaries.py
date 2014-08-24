#! /usr/bin/env python3

from helper.easierlife import BASE_DIR

# Load an example dictionary
# First column is doc id, second is sentence id, third is entity
def load_examples_dictionary(filename):
    examples = set()
    with open(filename, 'rt') as examples_dict_file:
        for line in examples_dict_file:
            examples.add(frozenset(line.rstrip().split("\t")))
    return examples

# Load the genes dictionary
def load_genes_dictionary(filename):
    genes_dict = dict()
    with open(filename, 'rt') as genes_dict_file:
        for line in genes_dict_file:
            tokens = line.strip().split("\t")
            # first token is name, the rest are synonyms
            name = tokens[0]
            for synonym in tokens:
                genes_dict[synonym] = name
    return genes_dict()

# Load a dictionary which is a set.
def load_set(filename):
    _set = set()
    with open(filename, 'rt') as set_file:
        for line in set_file:
            line = line.rstrip()
            _set.add(line)
    return _set

# Load a dictionary which is a set, but convert the entries to lower case
def load_set_lower_case(filename):
    case_set = load_set(filename)
    lower_case_set = set()
    for entry in case_set:
        lower_case_set.add(entry.lower())
    return lower_case_set

## Dictionaries
GENES_DICT_FILENAME = BASE_DIR + "/dicts/hugo_synonyms.tsv"
ENGLISH_DICT_FILENAME = BASE_DIR + "/dicts/english_words.tsv"
NIH_GRANTS_DICT_FILENAME = BASE_DIR + "/dicts/grant_codes_nih.tsv"
NSF_GRANTS_DICT_FILENAME = BASE_DIR + "/dicts/grant_codes_nsf.tsv"
MED_ACRONS_DICT_FILENAME = BASE_DIR + "/dicts/med_acronyms_pruned.tsv"
POS_GENE_MENTIONS_DICT_FILENAME = BASE_DIR + "/dicts/positive_gene_mentions.tsv"
NEG_GENE_MENTIONS_DICT_FILENAME= BASE_DIR + "/dicts/negative_gene_mentions.tsv"

## Dictionary of dictionaries. First argument is the filename, second is the
## function to call to load the dictionary. The function must take the filename as
## input and return an object like a dictionary, or a set, or a list, ...
dictionaries = dict()
dictionaries["genes"] = [GENES_DICT_FILENAME, load_genes_dictionary]
dictionaries["english"] = [ENGLISH_DICT_FILENAME, load_set_lower_case]
dictionaries["nih_grants"] = [NIH_GRANTS_DICT_FILENAME, load_set]
dictionaries["nsf_grants"] = [NSF_GRANTS_DICT_FILENAME, load_set]
dictionaries["med_acrons"] = [MED_ACRONS_DICT_FILENAME, load_set]
dictionaries["pos_gene_mentions"] = [POS_GENE_MENTIONS_DICT_FILENAME, load_examples_dictionary]
dictionaries["neg_gene_mentions"] = [NEG_GENE_MENTIONS_DICT_FILENAME, load_examples_dictionary]

## Load a dictionary using the appropriate filename and load function
def load_dict(dict_name):
    if dict_name not in dictionaries:
        return None
    filename = dictionaries[dict_name][0]
    load = dictionaries[dict_name][1]
    return load(filename)

