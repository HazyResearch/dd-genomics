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
    return genes_dict

# Load the HPOterms dictionary
# Terms are converted to lower case
def load_hpoterms_dictionary(filename):
    hpoterms_dict = dict()
    with open(filename, 'rt') as hpoterms_dict_file:
        for line in hpoterms_dict_file:
            tokens = line.strip().split("\t")
            # 1st token is name, 2nd is description, 3rd is 'C' and 4th is
            # (presumably) the distance from the root of the DAG.
            name = tokens[0]
            description = tokens[1]
            # Skip "All"
            # XXX (Matteo) There may be more generic terms that we want to skip
            if description == "All":
                continue
            description_words = description.split()
            variants = get_variants(description_words)
            for variant in variants:
                hpoterms_dict[variant.lower()] = name
    return hpoterms_dict

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

# Load a dictionary which is a set of pairs, where the pairs are frozensets
def load_set_pairs(filename):
    pair_set = set()
    with open(filename, 'rt') as set_file:
        for line in set_file:
            tokens = line.rstrip.split("\t")
            pair_set.add(frozenset(tokens))
    return pair_set

## Dictionaries
GENES_DICT_FILENAME = BASE_DIR + "/dicts/hugo_synonyms.tsv"
ENGLISH_DICT_FILENAME = BASE_DIR + "/dicts/english_words.tsv"
GENEHPOTERM_DICT_FILENAME = BASE_DIR + "/dicts/genes_to_hpo_terms_with_synonyms.tsv"
HPOTERMS_DICT_FILENAME = BASE_DIR + "/dicts/hpo_terms.tsv"
MED_ACRONS_DICT_FILENAME = BASE_DIR + "/dicts/med_acronyms_pruned.tsv"
NIH_GRANTS_DICT_FILENAME = BASE_DIR + "/dicts/grant_codes_nih.tsv"
NSF_GRANTS_DICT_FILENAME = BASE_DIR + "/dicts/grant_codes_nsf.tsv"
STOPWORDS_DICT_FILENAME = BASE_DIR + "/dicts/english_stopwords.tsv"
POS_GENE_MENTIONS_DICT_FILENAME = BASE_DIR + "/dicts/positive_gene_mentions.tsv"
NEG_GENE_MENTIONS_DICT_FILENAME= BASE_DIR + "/dicts/negative_gene_mentions.tsv"

## Dictionary of dictionaries. First argument is the filename, second is the
## function to call to load the dictionary. The function must take the filename as
## input and return an object like a dictionary, or a set, or a list, ...
dictionaries = dict()
dictionaries["genes"] = [GENES_DICT_FILENAME, load_genes_dictionary]
dictionaries["english"] = [ENGLISH_DICT_FILENAME, load_set_lower_case]
dictionaries["genehpoterms"] = [GENEHPOTERM_DICT_FILENAME, load_set_pairs]
dictionaries["hpoterms"] = [HPOTERMS_DICT_FILENAME,load_hpoterms_dictionary ]
dictionaries["nih_grants"] = [NIH_GRANTS_DICT_FILENAME, load_set]
dictionaries["nsf_grants"] = [NSF_GRANTS_DICT_FILENAME, load_set]
dictionaries["med_acrons"] = [MED_ACRONS_DICT_FILENAME, load_set]
dictionaries["stopwords"] = [STOPWORDS_DICT_FILENAME, load_set]
dictionaries["pos_gene_mentions"] = [POS_GENE_MENTIONS_DICT_FILENAME, load_examples_dictionary]
dictionaries["neg_gene_mentions"] = [NEG_GENE_MENTIONS_DICT_FILENAME, load_examples_dictionary]

## Load a dictionary using the appropriate filename and load function
def load_dict(dict_name):
    if dict_name not in dictionaries:
        return None
    filename = dictionaries[dict_name][0]
    load = dictionaries[dict_name][1]
    return load(filename)

## Given a list of words, return a list of variants built by splitting words that contain the separator.
## An example is more valuable:
## let words = ["the", "cat/dog", "is", "mine"], the function would return ["the
## cat is mine", "the dog is mine"]
## XXX (Matteo) Maybe goes in a different module
def get_variants(words, separator="/"):
    if len(words) == 0:
        return []
    variants = []
    base = []
    i = 0
    # Look for a word containing a "/"
    while words[i].find(separator) == -1:
        base.append(words[i])
        i += 1
        if i == len(words):
            break
    # If we found a word containing a "/", call recursively
    if i < len(words):
        variants_starting_words = words[i].split("/")
        following_variants = get_variants(words[i+1:])
        for variant_starting_word in variants_starting_words:
            variant_base = base + [variant_starting_word]
            if len(following_variants) > 0:
                for following_variant in following_variants:
                    variants.append(" ".join(variant_base +[following_variant]))
            else:
                variants.append(" ".join(variant_base))
    else:
        variants = [" ".join(base)]
    return variants

