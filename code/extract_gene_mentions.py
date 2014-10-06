#! /usr/bin/env python3
#
# Extract gene mention candidates, add features, and
# perform distant supervision
#

import fileinput
import re

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.dictionaries import load_dict
from helper.easierlife import get_all_phrases_in_sentence, \
    get_dict_from_TSVline, TSVstring2list, TSVstring2dict, no_op

DOC_ELEMENTS = frozenset(
    ["figure", "table", "figures", "tables", "fig", "fig.", "figs", "figs."])
INDIVIDUALS = frozenset(["individual", "individuals"])
TYPES = frozenset(["group", "type", "class", "method"])

GENE_KEYWORDS = frozenset([
    "gene", "protein", "tumor", "domain", "sequence", "sequences", "alignment",
    "expression", "mrna", "rna", "rrna", "dna", "cdna", "knockout",
    "knockdown", "recruitment", "hybridization", "isoform", "receptor",
    "receptors", "mutation", "mutations", "molecule", "molecules", "enzyme",
    "peptide", "staining", "binding", "allele", "alignment", "region",
    "transcribe", "deletion", "overexpression", "intron", "level", "T-cell",
    "inhibitor", "resistance", "serum", "DD-genotype", "genotype",
    "interaction", "function", "marker", "activation", "recruitment",
    "transcript", "antibody", "down-regulation", "proliferation",
    "polymorphism", "sumoylation", "enhancer", "histone", "hexons",
    "transporter", "hexon", "biomarker", "repressor", "promoter", "carcinoma",
    "haplotype", "haplotypes", "regulator", "downregulation", "lymphoma",
    "sarcoma", "kinase", "cancer", "tumours", "tumour", "inducer" "morpheein",
    "methylation", "fibrosarcoma", "protooncogene", "antigen" "antigene",
    "pseudogene", "agonist", "phosphorylation", "inducer", "mutant",
    "know-down", "knock-out", "excision", "hypermethylation",
    "over-expression", "adaptor", "functionality", "effector", "determinant",
    "motif", "factor", "release", "duplication", "variation", "kinesin",
    "ribonuclease", "antagonist", "pathway", "retention", "oligomerization",
    "subunit", "co-activator", "translocation", "sequestration", "activation",
    "location", "breakdown", "up-regulation", "acetylation", "complex",
    "ligand", "co-expression", "coexpression", "dysfunction", "transducer",
    "nucleotide", "modification", "variant", "signaling", "complex",
    "transcription", "human", "backbone", "oncoprotein", "locus", "moiety",
    "cluster", "homology", "proto-oncogene", "mammalian", "anti-gene",
    "transgene", "sirnas", "sirna", "siRNA", "siRNAs", "cleavage",
    "polymorphism", "induction", "enrichment", "determinant", "role"])


def check_negative_example(mention, sentence):
    example_key_1 = frozenset([sentence.doc_id, mention.entity])
    example_key_2 = frozenset([sentence.doc_id, mention.words[0].word])
    if (example_key_1 in neg_mentions_dict and
            (neg_mentions_dict[example_key_1] is None or sentence.sent_id in
             neg_mentions_dict[example_key_1])) or \
            (example_key_2 in neg_mentions_dict and
             (neg_mentions_dict[example_key_2] is None or sentence.sent_id
              in neg_mentions_dict[example_key_2])):
        mention.add_feature("IS_NEGATIVE_EXAMPLE")
        mention.is_correct = False


# Perform the supervision
def supervise(mention, sentence):
    # Not correct if it is in our collection of negative examples
    check_negative_example(mention, sentence)
    if mention.is_correct is False:
        return
    # Correct if it is in our collection of positive examples
    example_key_1 = frozenset([sentence.doc_id, mention.entity])
    example_key_2 = frozenset([sentence.doc_id, mention.words[0].word])
    if (example_key_1 in pos_mentions_dict and
            (pos_mentions_dict[example_key_1] is None or sentence.sent_id in
                pos_mentions_dict[example_key_1])) or \
            (example_key_2 in pos_mentions_dict and
                (pos_mentions_dict[example_key_2] is None or sentence.sent_id
                    in pos_mentions_dict[example_key_2])):
        mention.is_correct = True
        return
    if "IS_DNA_TRIPLET" in mention.features:
        mention.is_correct = False
        return
    # Not correct if the previous word is one of the following keywords
    # denoting a figure, a table, or an individual
    if "IS_AFTER_DOC_ELEMENT" in mention.features:
        mention.is_correct = False
        return
    if "IS_AFTER_TYPE" not in mention.features and \
            "COMES_AFTER_LOCATION" not in mention.features and \
            "COMES_AFTER_DOC_ELEMENT" not in mention.features:
        if "EXT_KEYWORD_SHORTEST_PATH_[gene]@nn" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[gene]nn@" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[promoter]nn@" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[protein]nn@" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[protein]nsubj@" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[binding]prep_with@" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[mrna]nn@" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[activation]nn@" in mention.features:
            mention.is_correct = True
            return
        if "IS_LONG_NAME" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[receptor]@nn" in mention.features:
            mention.is_correct = True
            return
        if "IS_LONG_ALPHANUMERIC_MAIN_SYMBOL" in mention.features:
            mention.is_correct = True
            return
        if "IS_HYPHENATED_SYMBOL" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[histone]@nn" in mention.features:
            mention.is_correct = True
            return
        if "EXT_KEYWORD_SHORTEST_PATH_[receptor]nn" in mention.features:
            mention.is_correct = True
            return
    if "EXT_KEYWORD_SHORTEST_PATH_[chromosome]@nn" in mention.features:
        mention.is_correct = False
        return
    if "IS_YEAR_RIGHT" in mention.features:
        mention.is_correct = False
        return
    if "IS_AFTER_INDIVIDUAL" in mention.features and \
            not mention.words[0].word.isalpha():
        mention.is_correct = False
        return
    if "IS_AFTER_TYPE" in mention.features:
        mention.is_correct = False
        return
    # Not correct if it is in a sentence that start with "Address(es)"
    if "IS_ADDRESS_SENTENCE" in mention.features:
        mention.is_correct = False
        return
    # Not correct if "T" and the next lemma is 'cell'.
    if len(mention.words) == 1 and mention.words[0].word == "T" and \
            mention.right_lemma == "cell":
        mention.is_correct = False
        return
    if len(mention.words) == 1 and \
            (mention.words[0].word == "X" or mention.words[0].word == "Y") and\
            mention.right_lemma == "chromosome":
        mention.is_correct = False
        return
    # A single letter and no English words in the sentence
    if len(mention.words) == 1 and len(mention.words[0].word) == 1 and \
            "NO_ENGLISH_WORDS_IN_SENTENCE" in mention.features:
        mention.is_correct = False
        return
    # Not correct if it's most probably a name.
    if "IS_BETWEEN_NAMES" in mention.features:
        mention.is_correct = False
        return
    # Comes after person and before "et", so it's probably a name
    if "COMES_AFTER_PERSON" in mention.features and \
            mention.right_lemma == "et":
        mention.is_correct = False
        return
    # Comes after person and before "," or ":", so it's probably a name
    if "COMES_AFTER_PERSON" in mention.features and \
            mention.words[-1].in_sent_idx + 1 < len(sentence.words) and \
            sentence.words[mention.words[-1].in_sent_idx + 1].word \
            in [",", ":"]:
        mention.is_correct = False
        return
    if "COMES_AFTER_PERSON" in mention.features and \
            "IS_HYPHENATE_SYMBOL" in mention.features:
        mention.is_correct = False
        return
    if "COMES_AFTER_PERSON" in mention.features and \
            "IS_PERSON" in mention.features:
        mention.is_correct = False
        return
    if "IS_GENE_ONTOLOGY" in mention.features:
        mention.is_correct = False
        return
    # Is a location and comes before a location so it's probably wrong
    if "IS_LOCATION" in mention.features and \
            "COMES_BEFORE_LOCATION" in mention.features:
        mention.is_correct = False
        return
    if "COMES_BEFORE_ET" in mention.features:
        mention.is_correct = False
    if mention.entity == "PROC":
        for feature in mention.features:
            if feature.startswith("EXT_VERB_PATH_[use]"):
                mention.is_correct = False
                return
    for feature in mention.features:
        if feature.startswith("EXT_VERB_PATH_[write]") and "paper" in feature:
                mention.is_correct = False
                return
        if feature.startswith("EXT_VERB_PATH_[contribute]") and \
                "reagent" in feature:
            mention.is_correct = False
            return
        if feature.startswith("EXT_VERB_PATH_[perform]") and \
                "experiment" in feature:
            mention.is_correct = False
            return
    if "IS_CONTRIBUTION_PHRASE" in mention.features:
        mention.is_correct = False
        return
    # if "IS_QUANTITY":
    #    mention.is_correct = False
    #    return
    # If it's "II", it's most probably wrong.
    if mention.words[0].word == "II":
        mention.is_correct = False
        return


# Add features to a gene mention
def add_features(mention, sentence):
    # There are no English words in the sentence
    # This may be useful to push down weird/junk sentences
    no_english_words = True
    for word in sentence.words:
        if len(word.word) > 2 and \
                (word.word in english_dict or
                 word.word.casefold() in english_dict):
            no_english_words = False
            break
    if no_english_words:
        mention.add_feature("NO_ENGLISH_WORDS_IN_SENTENCE")
        return
    phrase = " ".join([x.word for x in sentence.words])
    if phrase.startswith("Performed the experiments :") or \
            phrase.startswith("Wrote the paper :") or \
            phrase.startswith("W'rote the paper :") or \
            phrase.startswith("Wlrote the paper") or \
            phrase.startswith("Contributed reagents") or \
            phrase.startswith("	Analyzed the data :"):
                mention.add_feature("IS_CONTRIBUTION_PHRASE")

    # The mention is a single word that is in the English dictionary
    # but we differentiate between lower case and upper case
    if len(mention.words) == 1 and \
            (mention.words[0].word.casefold() in english_dict or
             mention.words[0].lemma.casefold() in english_dict) and \
            len(mention.words[0].word) > 2:
        if mention.words[0].word.isupper():
            pass
        #    mention.add_feature('IS_ENGLISH_WORD_UPP_CASE')
        elif mention.words[0].word.islower():
            mention.add_feature('IS_ENGLISH_WORD_LOW_CASE')
        elif mention.words[0].word[1:].islower():
            mention.add_feature("IS_ENGLISH_WORD_CAPITALIZED")
        else:
            mention.add_feature('IS_ENGLISH_WORD_MIXED_CASE')
    if len(mention.words) == 1 and mention.words[0].word.isalpha() and \
            mention.words[0].word.casefold() != mention.words[0].word and \
            not mention.words[0].word.isupper() and \
            mention.words[0].word.casefold() not in english_dict and \
            mention.words[0].lemma.casefold() not in english_dict:
                mention.add_feature("IS_MIXED_CASE_NON_ENGLISH")
    # The NER is an organization, or a location, or a person
    # XXX (Matteo) 20140905 Taking out ORGANIZATION, as it seems to induce
    # false negatives.
    if len(mention.words) == 1 and \
            mention.words[0].ner in ["LOCATION", "PERSON"]:
        mention.add_feature("IS_" + mention.words[0].ner)
    # The word comes after an organization, or a location, or a person. We skip
    # commas as they may trick us
    comes_after = None
    loc_idx = mention.wordidxs[0] - 1
    while loc_idx >= 0 and sentence.words[loc_idx].lemma == ",":
        loc_idx -= 1
    if loc_idx >= 0 and \
            sentence.words[loc_idx].ner in \
            ["ORGANIZATION", "LOCATION", "PERSON"] and \
            sentence.words[loc_idx].word not in merged_genes_dict:
        # mention.add_feature("COMES_AFTER_" + sentence.words[loc_idx].ner)
        comes_after = sentence.words[loc_idx].ner
    # The word comes before an organization, or a location, or a person. We
    # skip commas, as they may trick us.
    comes_before = None
    loc_idx = mention.wordidxs[-1] + 1
    while loc_idx < len(sentence.words) and \
            sentence.words[loc_idx].lemma == ",":
        loc_idx += 1
    if loc_idx < len(sentence.words) and \
            sentence.words[loc_idx].ner in \
            ["ORGANIZATION", "LOCATION", "PERSON"] and \
            sentence.words[loc_idx].word not in merged_genes_dict:
        # mention.add_feature("COMES_BEFORE_" + sentence.words[loc_idx].ner)
        comes_before = sentence.words[loc_idx].ner
    if loc_idx < len(sentence.words) and sentence.words[loc_idx] == "et":
        mention.add_feature("COMES_BEFORE_ET")
    # The word is between two words that are an organization, or a location or
    # a person
    if comes_before and comes_after:
        # mention.add_feature("IS_BETWEEN_" + comes_after + "_" + comes_before)
        mention.add_feature("IS_BETWEEN_NAMES")
    elif comes_before:
        mention.add_feature("COMES_BEFORE_" + comes_before)
    elif comes_after:
        mention.add_feature("COMES_AFTER_" + comes_after)
    # The word comes after a "document element" (e.g., table, or figure)
    prev_word = sentence.get_prev_wordobject(mention)
    if prev_word and prev_word.word.casefold() in DOC_ELEMENTS:
        mention.add_feature("IS_AFTER_DOC_ELEMENT")
    if prev_word and prev_word.word.casefold() in INDIVIDUALS and \
            not mention.words[0].word.isalpha() and \
            not len(mention.words[0].word) > 4:
        mention.add_feature("IS_AFTER_INDIVIDUAL")
    if prev_word and prev_word.lemma.casefold() in TYPES and \
            set(mention.words[0].word).issubset(set(["I", "V"])):
        mention.add_feature("IS_AFTER_TYPE")
    if len(mention.words) == 1:
        if mention.words[0].word in inverted_long_names:
            # Long name
            mention.add_feature("IS_LONG_NAME")
            if "COMES_AFTER_PERSON" in mention.features:
                mention.features.remove("COMES_AFTER_PERSON")
            if "COMES_AFTER_ORGANIZATION" in mention.features:
                mention.features.remove("COMES_AFTER_ORGANIZATION")
        entity_is_word = False
        entity_in_dict = False
        for entity in mention.entity.split("|"):
            if entity == mention.words[0].word:
                entity_is_word = True
            if entity in merged_genes_dict:
                entity_in_dict = True
        if entity_is_word and entity_in_dict and \
                "IS_BETWEEN_NAMES" not in mention.features and \
                len(mention.words[0].word) > 1:
            # The mention is a 'main' symbol
            # mention.add_feature('IS_MAIN_SYMBOL')
            if mention.words[0].word.isalnum() and \
                    not mention.words[0].word.isalpha():
                if len(mention.words[0].word) >= 4:
                    mention.add_feature("IS_LONG_ALPHANUMERIC_MAIN_SYMBOL")
                else:
                    is_letter_plus_number = False
                    try:
                        int(mention.words[0].word[1:])
                        is_letter_plus_number = True
                    except:
                        is_letter_plus_number = False
                    if is_letter_plus_number:
                        mention.add_feature(
                            "IS_LETTER_NUMBER_MAIN_SYMBOL_[{}]".format(
                                mention.words[0].word))
                    else:
                        mention.add_feature(
                            "IS_SHORT_ALPHANUMERIC_MAIN_SYMBOL_[{}]".format(
                                mention.words[0].word))
            elif len(mention.words[0].word) >= 4:
                mention.add_feature("IS_LONG_MAIN_SYMBOL_[{}]".format(
                    mention.words[0].word))
                if "COMES_AFTER_PERSON" in mention.features:
                    mention.features.remove("COMES_AFTER_PERSON")
                if "COMES_AFTER_ORGANIZATION" in mention.features:
                    mention.features.remove("COMES_AFTER_ORGANIZATION")
        elif entity_in_dict or mention.words[0].word in merged_genes_dict:
            if len(mention.words[0].word) > 3 and \
                    mention.words[0].word.casefold() == mention.words[0].word \
                    and not re.match("^p[0-9]+$", mention.words[0].word):
                # Long name
                mention.add_feature("IS_LONG_NAME")
                if "COMES_AFTER_PERSON" in mention.features:
                    mention.features.remove("COMES_AFTER_PERSON")
                if "COMES_AFTER_ORGANIZATION" in mention.features:
                    mention.features.remove("COMES_AFTER_ORGANIZATION")
            elif mention.words[0].word in inverted_long_names:
                # Long name
                mention.add_feature("IS_LONG_NAME")
                if "COMES_AFTER_PERSON" in mention.features:
                    mention.features.remove("COMES_AFTER_PERSON")
                if "COMES_AFTER_ORGANIZATION" in mention.features:
                    mention.features.remove("COMES_AFTER_ORGANIZATION")
            elif "-" in mention.words[0].word and \
                    "COMES_AFTER_PERSON" not in mention.features:
                mention.add_feature("IS_HYPHENATED_SYMBOL")
            elif mention.words[0].word.casefold().endswith("alpha") or \
                    mention.words[0].word.casefold().endswith("beta") or \
                    mention.words[0].word.casefold().endswith("gamma"):
                mention.add_feature("ENDS_WITH_GREEK")
            elif re.match("^p[0-9][0-9]$", mention.words[0].word):
                mention.add_feature("IS_PXX_SYMBOL_[{}]".format(
                    mention.words[0].word))
            elif len(mention.words[0].word) == 1:
                mention.add_feature("IS_SINGLE_LETTER")
            elif mention.words[0].word.isalnum() and \
                    not mention.words[0].word.isalpha():
                if len(mention.words[0].word) >= 4:
                    mention.add_feature(
                        "IS_LONG_ALPHANUMERIC_ALTERN_SYMBOL_[{}]".format(
                            mention.words[0].word))
            elif len(mention.words[0].word) >= 4:
                mention.add_feature("IS_LONG_ALTERN_SYMBOL_[{}]".format(
                    mention.words[0].word))
                # The mention is a synonym symbol
            #    mention.add_feature('IS_SYNONYM')
    elif " ".join([word.word for word in mention.words]) in \
            inverted_long_names:
        # Long name
        mention.add_feature("IS_LONG_NAME")
        if "COMES_AFTER_PERSON" in mention.features:
            mention.features.remove("COMES_AFTER_PERSON")
        if "COMES_AFTER_ORGANIZATION" in mention.features:
            mention.features.remove("COMES_AFTER_ORGANIZATION")
    else:
        for entity in mention.entity.split("|"):
            if entity in merged_genes_dict:
                # The mention is a long name
                mention.add_feature('IS_LONG_NAME')
                if "COMES_AFTER_PERSON" in mention.features:
                    mention.features.remove("COMES_AFTER_PERSON")
                if "COMES_AFTER_ORGANIZATION" in mention.features:
                    mention.features.remove("COMES_AFTER_ORGANIZATION")
                break
    # The labels and the NERs on the shortest dependency path
    # between a verb and the mention word.
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma.isalpha() and re.search('^VB[A-Z]*$', word2.pos) and \
                word2.lemma != 'be':
            p = sentence.get_word_dep_path(mention.wordidxs[0],
                                           word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw:
        mention.add_feature('EXT_VERB_PATH_[' + minw + ']' + minp)
        # mention.add_feature('VERB_PATH_[' + minw + ']')
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma in GENE_KEYWORDS:
            p = sentence.get_word_dep_path(mention.wordidxs[0],
                                           word2.in_sent_idx)
            # mention.add_feature("KEYWORD_[" + word2.lemma + "]")
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    # Special feature for the keyword on the shortest dependency path
    if minw:
        mention.add_feature('EXT_KEYWORD_SHORTEST_PATH_[' + minw + ']' + minp)
        # mention.add_feature('KEYWORD_SHORTEST_PATH_[' + minw + ']')
    # else:
        # mention.add_feature("NO_KEYWORDS")
    # The word appears many times (more than 4) in the sentence
    if len(mention.words) == 1 and \
            [w.word for w in sentence.words].count(mention.words[0].word) > 4:
        mention.add_feature("APPEARS_MANY_TIMES_IN_SENTENCE")
    # There are many PERSONs/ORGANIZATIONs/LOCATIONs in the sentence
    for ner in ["PERSON", "ORGANIZATION", "LOCATION"]:
        if [x.lemma for x in sentence.words].count(ner) > 4:
            mention.add_feature("MANY_{}_IN_SENTENCE".format(ner))
    # There are no English words in the sentence
    # This may be useful to push down weird/junk sentences
    no_english_words = True
    for word in sentence.words:
        if len(word.word) > 2 and \
                (word.word in english_dict or
                 word.word.casefold() in english_dict):
            no_english_words = False
            break
    if no_english_words:
        mention.add_feature("NO_ENGLISH_WORDS_IN_SENTENCE")
    if mention.words[0].word == "II":
        mention.add_feature("IS_ROMAN_II")
    if sentence.words[0].word.casefold() in ["address", "addresses"]:
        mention.add_feature("IS_ADDRESS_SENTENCE")
    if mention.words[0].word == "BLAST":
        mention.add_feature("IS_BLAST")
    if "NO_ENGLISH_WORDS_IN_SENTENCE" not in mention.features:
        if len(mention.words[0].word) == 3 and \
                set(mention.words[0].word) <= set("ACGT"):
            idx = mention.wordidxs[0] - 1
            if idx > 0:
                if set(sentence.words[idx].word) <= set("ACGT"):
                    mention.add_feature("IS_DNA_TRIPLET")
            idx = mention.wordidxs[-1] + 1
            if idx < len(sentence.words):
                if set(sentence.words[idx].word) <= set("ACGT"):
                    mention.add_feature("IS_DNA_TRIPLET")
        idx = mention.wordidxs[0] - 1
        if idx >= 0:
            if sentence.words[idx].word == "%":
                mention.add_feature("IS_QUANTITY_[{}]".format(
                    mention.words[0].word))
        idx = mention.wordidxs[-1] + 1
        if idx < len(sentence.words):
            if sentence.words[idx].word == "=":
                mention.add_feature("IS_QUANTITY_[{}]".format(
                    mention.words[0].word))
            if sentence.words[idx].word == ":":
                try:
                    float(sentence.words[idx + 1].word)
                    mention.add_feature("IS_QUANTITY_[{}]".format(
                        mention.words[0].word))
                except:
                    pass
        # The lemma on the left of the mention, if present, provided it's
        # alphanumeric but not a number
        idx = mention.wordidxs[0] - 1
        gene_on_left = None
        gene_on_right = None
        while idx >= 0 and \
                ((((not sentence.words[idx].lemma.isalnum() and not
                    sentence.words[idx] in merged_genes_dict) or
                 (not sentence.words[idx].word.isupper() and
                  sentence.words[idx].lemma in stopwords_dict)) and
                 not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word)
                 and not sentence.words[idx] in merged_genes_dict) or
                 len(sentence.words[idx].lemma) == 1):
            idx -= 1
        if idx >= 0:
            mention.left_lemma = sentence.words[idx].lemma
            if sentence.words[idx].word in merged_genes_dict and \
                    len(sentence.words[idx].word) > 3:
                # mention.add_feature("GENE_ON_LEFT")
                gene_on_left = sentence.words[idx].word
            try:
                year = float(sentence.words[idx].word)
                if round(year) == year and year > 1950 and year <= 2014:
                    mention.add_feature("IS_YEAR_LEFT")
                # else:
                #    mention.add_feature("IS_NUMBER_LEFT")
            except:
                pass
        # The word on the right of the mention, if present, provided it's
        # alphanumeric but not a number
        idx = mention.wordidxs[-1] + 1
        while idx < len(sentence.words) and \
            ((((not sentence.words[idx].lemma.isalnum() and not
                sentence.words[idx] in merged_genes_dict) or
                (not sentence.words[idx].word.isupper() and
                 sentence.words[idx].lemma in stopwords_dict)) and
                not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word)
                and not sentence.words[idx] in merged_genes_dict) or
                len(sentence.words[idx].lemma) == 1):
            idx += 1
        if idx < len(sentence.words):
            mention.right_lemma = sentence.words[idx].lemma
            if sentence.words[idx].word in merged_genes_dict and \
                    len(sentence.words[idx].word) > 3:
                # mention.add_feature("GENE_ON_RIGHT")
                gene_on_right = sentence.words[idx].word
            try:
                year = float(sentence.words[idx].word)
                if round(year) == year and year > 1950 and year <= 2014:
                    mention.add_feature("IS_YEAR_RIGHT")
                # else:
                #    mention.add_feature("IS_NUMBER_RIGHT")
            except:
                pass
        if gene_on_left and gene_on_right:
            mention.add_feature("IS_BETWEEN_GENES")
        elif gene_on_left:
            mention.add_feature("GENE_ON_LEFT")
        elif gene_on_right:
            mention.add_feature("GENE_ON_RIGHT")
    if len(mention.words) == 1 and mention.words[0].word == "F5":
        mention.add_feature("IS_F5")
    if len(mention.words) == 1 and mention.words[0].word == "GO":
        try:
            if sentence.words[mention.words[0].in_sent_idx + 1][0] == ":":
                mention.add_feature("IS_GENE_ONTOLOGY")
        except:
            pass


# Return a list of mention candidates extracted from the sentence
def extract(sentence):
    mentions = []
    global random_examples
    # The following set keeps a list of indexes we already looked at and which
    # contained a mention
    history = set()
    words = sentence.words
    sentence_is_upper = False
    if " ".join([x.word for x in words]).isupper():
        sentence_is_upper = True
    # Scan all subsequences of the sentence
    for start, end in get_all_phrases_in_sentence(sentence,
                                                  max_mention_length):
        if start in history or end in history:
                continue
        phrase = " ".join([word.word for word in words[start:end]])
        if sentence_is_upper:
            phrase = phrase.casefold()
        mention = None
        # If the phrase is in the dictionary, then is a mention candidate
        if len(phrase) > 1 and phrase in merged_genes_dict:
            mention = Mention("GENE",
                              "|".join(merged_genes_dict[phrase]),
                              words[start:end])
            add_features(mention, sentence)
            mentions.append(mention)
            # Add to history
            for i in range(start, end):
                history.add(i)
    return mentions


# Load the dictionaries that we need
merged_genes_dict = load_dict("merged_genes")
english_dict = load_dict("english")
stopwords_dict = load_dict("stopwords")
pos_mentions_dict = load_dict("pos_gene_mentions")
neg_mentions_dict = load_dict("neg_gene_mentions")
med_acrons_dict = load_dict("med_acrons")
long_names_dict = load_dict("long_names")
inverted_long_names = load_dict("inverted_long_names")
max_mention_length = 0
for key in merged_genes_dict:
    length = len(key.split())
    if length > max_mention_length:
        max_mention_length = length
# doubling to take into account commas and who knows what
max_mention_length *= 2
if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "bounding_boxes", "acronyms", "definitions"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list, TSVstring2list, TSVstring2dict])
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Change the keys of the definition dictionary to be the acronyms
            if "acronyms" in line_dict:
                new_def_dict = dict()
                for i in range(len(line_dict["acronyms"])):
                    new_def_dict[line_dict["acronyms"][i]] = \
                        line_dict["definitions"]["TSV_" + str(i)]
                line_dict["definitions"] = new_def_dict
                # Remove duplicates from definitions
                if "definitions" in line_dict:
                    for acronym in line_dict["definitions"]:
                        line_dict["definitions"][acronym] = frozenset(
                            [x.casefold() for x in
                                line_dict["definitions"][acronym]])
            # Get list of mentions candidates in this sentence
            mentions = extract(sentence)
            # Supervise according to the mention type
            for mention in mentions:
                if "acronyms" in line_dict and \
                        "IS_LONG_NAME" not in mention.features:
                    is_acronym = False
                    for acronym in line_dict["acronyms"]:
                        if mention.words[0].word == acronym:
                            is_acronym = True
                            break
                    # Only process as acronym if that's the case
                    if is_acronym and \
                            "NO_ENGLISH_WORDS_IN_SENTENCE" not in \
                            mention.features:
                        contains_gene_protein = False
                        try:
                            defs = line_dict["definitions"][
                                mention.words[0].word]
                        except:
                            continue
                        for definition in defs:
                            if definition in merged_genes_dict:
                                if "IS_BETWEEN_NAMES" not in mention.features \
                                        and "NO_ENGLISH_WORDS_IN_SENTENCE" \
                                        not in mention.features:
                                    mention.add_feature(
                                        "COMES_WITH_EXACT_LONG_NAME")
                                    mention.is_correct = True
                                break
                            else:
                                try:
                                    definition.index(" gene")
                                    contains_gene_protein = True
                                except:
                                    pass
                                try:
                                    definition.index(" protein")
                                    contains_gene_protein = True
                                except:
                                    pass
                        if mention.is_correct is None \
                                and contains_gene_protein:
                            mention.add_feature(
                                "DEF_CONTAINS_GENE_PROT_[{}]".format(
                                    mention.words[0].word))
                        if mention.is_correct is None and \
                                not contains_gene_protein:
                            mention.type = "ACRONYM"
                            mention.add_feature("NOT_KNOWN_ACRONYM_" +
                                                mention.words[0].word)
                            mention.is_correct = False
                    else:  # Sentence contains acronym but not here
                        supervise(mention, sentence)
                else:  # not random and not acronyms in sentence
                    supervise(mention, sentence)
            for mention in mentions:
                print(mention.tsv_dump())
