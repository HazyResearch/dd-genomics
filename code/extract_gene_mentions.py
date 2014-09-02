#! /usr/bin/env python3
#
# Extract gene mention candidates, add features, and
# perform distant supervision
#

import fileinput
import json
import random

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from helper.dictionaries import load_dict
from helper.easierlife import get_all_phrases_in_sentence, get_dict_from_TSVline, TSVstring2list, no_op

RANDOM_EXAMPLES_PROB = 0.01
RANDOM_EXAMPLES_QUOTA = 1000
ACRONYMS_QUOTA = 1000
ACRONYMS_PROB = 0.01
false_acronyms = 0
random_examples = 0

DOC_ELEMENTS_OR_INDIVIDUALS =["figure", "table", "figures", "tables", "fig",
"fig.", "figs", "figs.", "individual", "individuals"]

## Perform the supervision
# We don't supervise anything as positive, except things that are in our
# collection of positive labelled examples because we have the geneRifs that
# will help us a lot since they are all positively labelled
def supervise(mention, sentence):
    # XXX (Matteo) The following commented code is from when we didn't use
    # geneRifs yet. It is inspired by similar code in the pharm repository.
    #
    # If the candidate mention a gene symbol in the supervision dictionary, and
    # not an English word, and not a medical acronym, and not a NIH or NSF
    # grant code, and not a Roman numeral then label it as correct, provided
    # we get head when we flip the coin
    #if random.random() < SUPERVISION_PROB and \
    #    mention_word.lower() not in english_dict and \
    #    mention_word not in med_acrons_dict and \
    #    mention_word not in nih_grants_dict and \
    #    mention_word not in nsf_grants_dict and \
    #    not re.match("^(IV|VI{,3}|I{1,4})$", mention_word):
    #        mention.is_correct = True
    #
    # Correct if it is in our collection of positive examples
    if frozenset([sentence.doc_id, str(sentence.sent_id), mention.entity]) in pos_mentions_dict or \
            frozenset([sentence.doc_id, str(sentence.sent_id), mention.words[0].word]) in pos_mentions_dict:
        mention.is_correct = True
    # Not correct if the previous word is one of the following keywords
    # denoting a figure, a table, or an individual
    if sentence.get_prev_wordobject(mention) != None and \
            sentence.get_prev_wordobject(mention).word.casefold() in DOC_ELEMENTS_OR_INDIVIDUALS:
        mention.is_correct = False
    # Not correct if it is in our collection of negative examples
    if frozenset([sentence.doc_id, str(sentence.sent_id), mention.entity]) in neg_mentions_dict or \
            frozenset([sentence.doc_id, str(sentence.sent_id), mention.words[0].word]) in neg_mentions_dict:
        mention.is_correct = False
    # If the sentence is less than 4 words, it probably doesn't contain
    # enough information to convey anything useful for the supervision, so let
    # the system learn what it is
    if len(sentence.words) < 4:
        mention.is_correct = None


## Add features to a gene mention
def add_features(mention, sentence):
    # The mention is a 'main' symbol:
    if len(mention.words) == 1 and mention.entity == mention.words[0].word and mention.entity in merged_genes_dict:
        mention.add_feature('IS_MAIN_SYMBOL')
    # The mention is a synonym symbol
    # XXX (Matteo) this is not entirely foolproof
    elif len(mention.words) == 1 and mention.entity in merged_genes_dict:
        mention.add_feature('IS_SYNONYM')
    # The mention is a long name
    elif mention.entity in merged_genes_dict:
        mention.add_feature('IS_LONG_NAME')
    # The mention is a single word that is in the English dictionary
    if len(mention.words) == 1 and mention.words[0].word.casefold() in english_dict or \
            mention.words[0].lemma in english_dict:
        mention.add_feature('IS_ENGLISH_WORD')
    # The NER is an organization, or a location, or a person
    if len(mention.words) == 1 and mention.words[0].ner in [ "ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("IS_" + mention.words[0].ner)
    # The word comes after an organization, or a location, or a person. We skip
    # commas as they may trick us
    comes_after = None
    idx = mention.wordidxs[0] - 1
    while idx >= 0 and sentence.words[idx].lemma == ",":
        idx -= 1
    if idx >= 0 and sentence.words[idx].ner in [ "ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("COMES_AFTER_" + sentence.words[idx].ner)
        comes_after = sentence.words[idx].ner
    # The word comes before an organization, or a location, or a person. We
    # skip commas, as they may trick us.
    comes_before = None
    idx = mention.wordidxs[-1] + 1
    while idx < len(sentence.words) and sentence.words[idx].lemma == ",":
        idx += 1
    if idx < len(sentence.words) and sentence.words[idx].ner in [ "ORGANIZATION", "LOCATION", "PERSON"]:
        mention.add_feature("COMES_BEFORE_" + sentence.words[idx].ner)
        comes_before = sentence.words[idx].ner
    # The word is between two words that are an organization, or a location or a person
    if comes_before and comes_after:
        mention.add_feature("IS_BETWEEN_" + comes_after + "_" + comes_before)
    # The word comes after a "document element" (e.g., table, or figure)
    prev_word = sentence.get_prev_wordobject(mention)
    if prev_word != None and prev_word.word.casefold() in DOC_ELEMENTS_OR_INDIVIDUALS:
        mention.add_feature("IS_AFTER_DOC_ELEMENT")
    # The labels and the NERs on the shortest dependency path
    # between a verb and the mention word.
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.pos.startswith('VB') and word2.lemma != 'be':
            p = sentence.get_word_dep_path(mention.wordidxs[0], word2.in_sent_idx)
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    if minw != None:
        mention.add_feature('EXT_VERB_PATH_[' + minw + ']' + minp)
        mention.add_feature('VERB_PATH_[' + minw + ']')
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word2 in sentence.words:
        if word2.lemma in ["gene", "genes", "protein", "proteins", "DNA",
                "rRNA", "cell", "cells", "tumor", "tumors", "domain",
                "sequence", "sequences", "alignment", "expression", "mRNA",
                "knockout", "recruitment", "hybridization", "isoform",
                "chromosome"]:
            p = sentence.get_word_dep_path(mention.wordidxs[0], word2.in_sent_idx)
            mention.add_feature("KEYWORD_[" + word2.lemma + "]")
            if len(p) < minl:
                minl = len(p)
                minp = p
                minw = word2.lemma
    # Special feature for the keyword on the shortest dependency path
    if minw != None:
        mention.add_feature('EXT_KEYWORD_SHORTEST_PATH_[' + minw + ']' + minp)
        mention.add_feature('KEYWORD_SHORTEST_PATH_[' + minw + ']')
    # The lemma on the left of the mention, if present, provided it's not a
    # ",", in which case we get the previous word
    idx = mention.wordidxs[0] - 1
    while idx >= 0 and sentence.words[idx].lemma == ",":
        idx -= 1
    if idx >= 0:
        mention.add_feature("WINDOW_LEFT_1_[{}]".format(
            sentence.words[idx].lemma))
    # The word on the right of the mention, if present, provided it's not a
    # ",", in which case we get the next word.
    idx = mention.wordidxs[-1] + 1
    while idx < len(sentence.words) and sentence.words[idx].lemma == ",":
        idx += 1
    if idx < len(sentence.words):
        mention.add_feature("WINDOW_RIGHT_1_[{}]".format(
            sentence.words[idx].lemma))
    # The word appears many times (more than 4) in the sentence
    if len(mention.words) == 1 and [w.word for w in sentence.words].count(mention.words[0].word) > 4:
        mention.add_feature("APPEARS_MANY_TIMES_IN_SENTENCE")
    # There are many PERSONs/ORGANIZATIONs/LOCATIONs in the sentence
    for ner in ["PERSON", "ORGANIZATION", "LOCATION"]:
        if [x.lemma for x in sentence.words].count(ner) > 4:
            mention.add_feature("MANY_{}_IN_SENTENCE".format(ner))


# Add features that are related to the entire set of mentions candidates
def add_features_to_all(mentions, sentence):
    # Number of other mentions in the sentence 
    for i in range(len(mentions)):
        for mention in mentions:
            mention.add_feature("{}_OTHER_MENTIONS_IN_SENTENCE".format(i))


## Return a list of mention candidates extracted from the sentence
def extract(sentence):
    mentions = []
    global random_examples
    # The following set keeps a list of indexes we already looked at and which
    # contained a mention
    history = set()
    words = sentence.words
    # Scan all subsequences of the sentence
    for start, end in get_all_phrases_in_sentence(sentence, max_mention_length):
        if start in history or end in history:
                continue
        phrase = " ".join([word.word for word in words[start:end]])
        mention = None
        # If the phrase is in the dictionary, then is a mention candidate
        if phrase in merged_genes_dict:
            mention = Mention("GENE",
                    "|".join(merged_genes_dict[phrase]), words[start:end])
            add_features(mention, sentence)
            mentions.append(mention)
            # Add to history
            for i in range(start, end + 1):
                history.add(i)
        else: # Potentially generate a random mention
            # Check whether it's a number, we do not want to generate a mention
            # with it.
            is_number = False
            try:
                float(phrase)
            except:
                pass
            else:
                continue
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
                len(sentence.words) > 5 and random.random() < RANDOM_EXAMPLES_PROB and \
                random_examples < RANDOM_EXAMPLES_QUOTA:
                # Generate a mention that somewhat resembles what a gene may look like,
                # or at least its role in the sentence.
                # This mention is supervised (as false) in the code calling this function
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
# XXX (Matteo) This dictionaries were used when we didn't have geneRifs to
# label mention candidates as positive. Now they're no longer needed. See also
# comment in supervise().
#nih_grants_dict = load_dict("nih_grants")
#nsf_grants_dict = load_dict("nsf_grants")
#med_acrons_dict = load_dict("med_acrons")
max_mention_length = 0
for key in merged_genes_dict:
    length = len(key.split())
    if length > max_mention_length:
        max_mention_length = length
max_mention_length *= 2 #doubling to take into account commas and who knows what

if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # This is for json
            #line_dict = json.loads(line)
            # This is for tsv
            line_dict = get_dict_from_TSVline(line, ["doc_id", "sent_id", "wordidxs",
            "words", "poses", "ners", "lemmas", "dep_paths", "dep_parents",
            "bounding_boxes", "acronym"], [no_op, int, lambda x :
                TSVstring2list(x, int), TSVstring2list, TSVstring2list,
                TSVstring2list, TSVstring2list, TSVstring2list, lambda x :
                TSVstring2list(x, int), TSVstring2list, no_op])
            sentence = Sentence(line_dict["doc_id"], line_dict["sent_id"],
                    line_dict["wordidxs"], line_dict["words"],
                    line_dict["poses"], line_dict["ners"], line_dict["lemmas"],
                    line_dict["dep_paths"], line_dict["dep_parents"],
                    line_dict["bounding_boxes"])
            # Get list of mentions candidates in this sentence
            mentions = extract(sentence)
            # Add features that use information about other mentions
            if len(mentions) > 1:
                add_features_to_all(mentions, sentence)
            # Supervise according to the mention type
            for mention in mentions:
                if "acronym" in line_dict:
                    if mention.words[0].word == line_dict["acronym"]:
                        mention.type = "ACRONYM"
                        if false_acronyms < ACRONYMS_QUOTA and \
                        random.random() < ACRONYMS_PROB:
                            mention.is_correct = False
                            false_acronyms += 1
                elif mention.type == "RANDOM":
                    # this is a randomly generated example that we assume
                    # to be false
                    mention.is_correct = False
                else:
                    supervise(mention, sentence)
                # Print!
                # This is for json
                #print(mention.json_dump())
                # This is for TSV
                print(mention.tsv_dump())

