#! /usr/bin/env python3
#
# Extract gene mention candidates, add features, and
# perform distant supervision
#

import fileinput
import random
import re

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.dictionaries import load_dict
from helper.easierlife import get_all_phrases_in_sentence, \
    get_dict_from_TSVline, TSVstring2list, TSVstring2dict, no_op

RANDOM_EXAMPLES_PROB = 0.01
RANDOM_EXAMPLES_QUOTA = 2000
ACRONYMS_QUOTA = 2000
ACRONYMS_PROB = 0.005
false_acronyms = 0
random_examples = 0

DOC_ELEMENTS = frozenset(
    ["figure", "table", "figures", "tables", "fig", "fig.", "figs", "figs."])
INDIVIDUALS = frozenset(["individual", "individuals"])

GENE_KEYWORDS = frozenset([
    "gene", "genes", "protein", "proteins", "DNA", "rRNA", "cell", "cells",
    "tumor", "tumors", "domain", "sequence", "sequences", "alignment",
    "expression", "mRNA", "knockout", "knockdown", "recruitment",
    "hybridization", "isoform", "chromosome", "receptor", "receptors",
    "mutation", "mutations", "molecule", "molecules", "enzyme", "peptide",
    "staining", "binding", "allele", "alignment", "region", "transcribe",
    "deletion", "bind", "regulate", "overexpression", "intron", "level",
    "promote", "T-cell", "inhibitor", "resistance", "serum", "DD-genotype",
    "genotype", "interaction", "function", "marker", "activation",
    "recruitment", "transcript", "antibody", "down-regulation",
    "proliferation", "activate", "polymorphism", "sumoylation",
    "enhancer"])


# Perform the supervision
# We don't supervise anything as positive, except things that are in our
# collection of positive labelled examples because we have the geneRifs that
# will help us a lot since they are all positively labelled
def supervise(mention, sentence):
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
    # Not correct if the previous word is one of the following keywords
    # denoting a figure, a table, or an individual
    if "IS_AFTER_DOC_ELEMENT" in mention.features:
        mention.is_correct = False
        return
    if "IS_AFTER_INDIVIDUAL" in mention.features:
        mention.is_correct = False
        return
    # Not correct if it is in our collection of negative examples
    if (example_key_1 in neg_mentions_dict and
            (neg_mentions_dict[example_key_1] is None or sentence.sent_id in
                neg_mentions_dict[example_key_1])) or \
            (example_key_2 in neg_mentions_dict and
                (neg_mentions_dict[example_key_2] is None or sentence.sent_id
                    in neg_mentions_dict[example_key_2])):
        mention.is_correct = False
        return
    # Not correct if "T" and the next lemma is 'cell'.
    if len(mention.words) == 1 and mention.words[0].word == "T" and \
            "WINDOW_RIGHT_1_[cell]" in mention.features:
        mention.is_correct = False
        return
    if len(mention.words) == 1 and mention.words[0].word == "X" and \
            "WINDOW_RIGHT_1_[chromosome]" in mention.features:
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
    if "COMES_BEFORE_PERSON" in mention.features:
        mention.is_correct = False
        return
    # Comes after person and before "et", so it's probably a name
    if "COMES_AFTER_PERSON" in mention.features and \
            "WINDOW_RIGHT_1_[et]" in mention.features:
        mention.is_correct = False
        return
    # Comes after person and before "," or ":", so it's probably a name
    if "COMES_AFTER_PERSON" in mention.features and \
            mention.words[-1].in_sent_idx + 1 < len(sentence.words) and \
            sentence.words[mention.words[-1].in_sent_idx + 1].word \
            in [",", ":"]:
        mention.is_correct = False
        return
    if "IS_LOCATION" in mention.features and \
            "COMES_BEFORE_LOCATION" in mention.features:
        mention.is_correct = False
        return
    # If it's "II", it's most probably wrong.
    if mention.words[0].word == "II":
        mention.is_correct = False
        return


# Add features to a gene mention
def add_features(mention, sentence):
    # The mention is a main symbol, or a synonym, or a long name
    if len(mention.words) == 1:
        entity_is_word = False
        entity_in_dict = False
        for entity in mention.entity.split("|"):
            if entity == mention.words[0].word:
                entity_is_word = True
            if entity in merged_genes_dict:
                entity_in_dict = True
        if entity_is_word and entity_in_dict:
            # The mention is a 'main' symbol
            mention.add_feature('IS_MAIN_SYMBOL')
        elif entity_in_dict or mention.words[0].word in merged_genes_dict:
            # XXX (Matteo) this is not entirely foolproof
            if mention.words[0].word.casefold() == mention.words[0].word:
                # Long name
                mention.add_feature("IS_LONG_NAME")
            else:
                # The mention is a synonym symbol
                mention.add_feature('IS_SYNONYM')
    else:
        for entity in mention.entity.split("|"):
            if entity in merged_genes_dict:
                # The mention is a long name
                mention.add_feature('IS_LONG_NAME')
                break
    # The mention is a single word that is in the English dictionary
    # but we differentiate between lower case and upper case
    if len(mention.words) == 1 and \
            (mention.words[0].word.casefold() in english_dict or
             mention.words[0].lemma.casefold() in english_dict) and \
            len(mention.words[0].word) > 2:
        if mention.words[0].word.isupper():
            mention.add_feature('IS_ENGLISH_WORD_UPP_CASE')
        else:
            mention.add_feature('IS_ENGLISH_WORD_LOW_CASE')
    # The NER is an organization, or a location, or a person
    # XXX (Matteo) 20140905 Taking out ORGANIZATION, as it seems to induce
    # false negatives.
    if len(mention.words) == 1 and \
            mention.words[0].ner in ["LOCATION", "PERSON"]:
        mention.add_feature("IS_" + mention.words[0].ner)
    # The word comes after an organization, or a location, or a person. We skip
    # commas as they may trick us
    comes_after = None
    idx = mention.wordidxs[0] - 1
    while idx >= 0 and sentence.words[idx].lemma == ",":
        idx -= 1
    if idx >= 0 and \
            sentence.words[idx].ner in ["ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("COMES_AFTER_" + sentence.words[idx].ner)
        comes_after = sentence.words[idx].ner
    # The word comes before an organization, or a location, or a person. We
    # skip commas, as they may trick us.
    comes_before = None
    idx = mention.wordidxs[-1] + 1
    while idx < len(sentence.words) and sentence.words[idx].lemma == ",":
        idx += 1
    if idx < len(sentence.words) and \
            sentence.words[idx].ner in ["ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("COMES_BEFORE_" + sentence.words[idx].ner)
        comes_before = sentence.words[idx].ner
    # The word is between two words that are an organization, or a location or
    # a person
    if comes_before and comes_after:
        mention.add_feature("IS_BETWEEN_" + comes_after + "_" + comes_before)
        mention.add_feature("IS_BETWEEN_NAMES")
    # The word comes after a "document element" (e.g., table, or figure)
    prev_word = sentence.get_prev_wordobject(mention)
    if prev_word and prev_word.word.casefold() in DOC_ELEMENTS:
        mention.add_feature("IS_AFTER_DOC_ELEMENT")
    if prev_word and prev_word.word.casefold() in INDIVIDUALS:
        mention.add_feature("IS_AFTER_INDIVIDUAL")
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
        mention.add_feature('VERB_PATH_[' + minw + ']')
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
        mention.add_feature('KEYWORD_SHORTEST_PATH_[' + minw + ']')
    else:
        mention.add_feature("NO_KEYWORDS")
    # The lemma on the left of the mention, if present, provided it's
    # alphanumeric but not a number
    idx = mention.wordidxs[0] - 1
    while idx >= 0 and \
            (not sentence.words[idx].lemma.isalnum() or
             sentence.words[idx].lemma in stopwords_dict) and \
            not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word):
        idx -= 1
    if idx >= 0:
        mention.add_feature("WINDOW_LEFT_1_[{}]".format(
            sentence.words[idx].lemma))
    # The word on the right of the mention, if present, provided it's
    # alphanumeric but not a number
    idx = mention.wordidxs[-1] + 1
    while idx < len(sentence.words) and \
            (not sentence.words[idx].lemma.isalnum() or
             sentence.words[idx].lemma in stopwords_dict) and \
            not re.match("^[0-9]+(.[0-9]+)?$", sentence.words[idx].word):
        idx += 1
    if idx < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_1_[{}]".format(
            sentence.words[idx].lemma))
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
     if len(mention.words) == 1 and mention.words[0].word == "T" and \
             "WINDOW_RIGHT_1_[cell]" in mention.features:
        mention.add_feature("IS_T_CELL")


# Add features that are related to the entire set of mentions candidates
# Must be called after supervision!!!
def add_features_to_all(mentions, sentence):
    # Number of distinct other mentions in the sentence that are not most
    # probably false
    not_names = set()
    for mention in mentions:
        if not mention.is_correct:
            not_names.add(frozenset(mention.words))
    for i in range(1, len(not_names)):
        for mention in mentions:
            mention.add_feature("{}_OTHER_MENTIONS_IN_SENTENCE".format(i))


# Return a list of mention candidates extracted from the sentence
def extract(sentence):
    mentions = []
    global random_examples
    # The following set keeps a list of indexes we already looked at and which
    # contained a mention
    history = set()
    words = sentence.words
    # Scan all subsequences of the sentence
    for start, end in get_all_phrases_in_sentence(sentence,
                                                  max_mention_length):
        if start in history or end in history:
                continue
        phrase = " ".join([word.word for word in words[start:end]])
        mention = None
        # If the phrase is in the dictionary, then is a mention candidate
        if phrase in merged_genes_dict:
            mention = Mention("GENE",
                              "|".join(merged_genes_dict[phrase]),
                              words[start:end])
            add_features(mention, sentence)
            mentions.append(mention)
            # Add to history
            for i in range(start, end):
                history.add(i)
        else:  # Potentially generate a random mention
            # Check whether it's a number, we do not want to generate a mention
            # with it.
            is_number = False
            try:
                float(phrase)
            except:
                pass
            else:
                is_number = True
            has_stop_words = False
            has_verbs = False
            in_merged_dict = False
            for word in words[start:end]:
                if word.word in stopwords_dict:
                    has_stop_words = True
                    break
                if word.pos.startswith("VB"):
                    has_verbs = True
                    break
                # XXX (Matteo) Not perfect. A subset of phrase may be in the
                # dict and we're not checking for this. Low probability, I'd
                # say.
                if word.word in merged_genes_dict:
                    in_merged_dict = True
                    break
            if phrase.isalnum() and not is_number and not has_stop_words and \
                    not has_verbs and not in_merged_dict and \
                    len(sentence.words) > 5 and \
                    random.random() < RANDOM_EXAMPLES_PROB and \
                    random_examples < RANDOM_EXAMPLES_QUOTA:
                # Generate a mention that somewhat resembles what a gene may
                # look like,
                # or at least its role in the sentence.
                # This mention is supervised (as false) in the code calling
                # this function
                mention = Mention("RANDOM", phrase, sentence.words[start:end])
                add_features(mention, sentence)
                random_examples += 1
                mentions.append(mention)
    return mentions


# Load the dictionaries that we need
merged_genes_dict = load_dict("merged_genes")
english_dict = load_dict("english")
stopwords_dict = load_dict("stopwords")
pos_mentions_dict = load_dict("pos_gene_mentions")
neg_mentions_dict = load_dict("neg_gene_mentions")
med_acrons_dict = load_dict("med_acrons")
# XXX (Matteo) This dictionaries were used when we didn't have geneRifs to
# label mention candidates as positive. Now they're no longer needed. See also
# comment in supervise().
# nih_grants_dict = load_dict("nih_grants")
# nsf_grants_dict = load_dict("nsf_grants")
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
                if mention.type == "RANDOM":
                    # this is a randomly generated example that we assume
                    # to be false
                    mention.add_feature("IS_RANDOM")
                    mention.is_correct = False
                elif "acronyms" in line_dict:
                    is_acronym = False
                    for acronym in line_dict["acronyms"]:
                        if mention.words[0].word == acronym:
                            is_acronym = True
                            break
                    # Only process as acronym if that's the case
                    if is_acronym:
                        for definition in \
                                line_dict["definitions"][
                                    mention.words[0].word]:
                            if definition in merged_genes_dict:
                                mention.add_feature("COMES_WITH_LONG_NAME")
                                mention.is_correct = True
                                break
                        if not mention.is_correct:
                            mention.type = "ACRONYM"
                            mention.add_feature("NOT_KNOWN_ACRONYM")
                            mention.add_feature("NOT_KNOWN_ACRONYM_" +
                                                mention.words[0].word)
                            for definition in \
                                    line_dict["definitions"][
                                        mention.words[0].word]:
                                mention.add_feature("NOT_KNOWN_ACRONYM_" +
                                                    definition)
                            for definition in \
                                    line_dict["definitions"][
                                        mention.words[0].word]:
                                if definition.casefold() in med_acrons_dict:
                                    mention.add_feature("IS_MED_ACRONYM")
                                    break
                            # Supervise anyway because it may be in set of
                            # negative examples but not processed by the
                            # following test
                            supervise(mention, sentence)
                            if false_acronyms < ACRONYMS_QUOTA and \
                                    random.random() < ACRONYMS_PROB:
                                mention.is_correct = False
                                false_acronyms += 1
                    else:  # Sentence contains acronym but not here
                        supervise(mention, sentence)
                else:  # not random and not acronyms in sentence
                    supervise(mention, sentence)
            # Add features that use information about other mentions
            if len(mentions) > 1:
                add_features_to_all(mentions, sentence)
            for mention in mentions:
                print(mention.tsv_dump())
