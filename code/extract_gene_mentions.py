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
    ["figure", "table", "figures", "tables", "fig", "fig.", "figs", "figs.",
     "file", "movie"])

INDIVIDUALS = frozenset(["individual", "individuals"])

TYPES = frozenset(["group", "type", "class", "method"])

# Keywords that are often associated with genes
GENE_KEYWORDS = frozenset([
    "acetylation", "activate", "activation", "adaptor", "agonist", "alignment",
    "allele", "antagonist", "antibody", "antigen", "antigene", "anti-gen",
    "anti-gene", "asynonymous", "backbone", "binding", "biomarker",
    "breakdown", "cancer", "carcinoma", "cdna", "cDNA", "cell", "cleavage",
    "cluster", "cnv", "coactivator", "co-activator", "co-expression",
    "coexpression", "complex", "dd-genotype", "DD-genotype", "deletion",
    "determinant", "dna", "domain", "down-regulation", "downregulation",
    "duplication", "dysfunction", "effector", "enhancer", "enrichment",
    "enzyme", "excision", "expression", "factor", "family", "fibrosarcoma",
    "function", "functionality", "gene", "genotype", "growth", "haplotype",
    "haplotypes", "heterozygous", "hexons", "hexon", "histone", "homologue",
    "homology", "homozygous" "human", "hypermetylation", "hybridization",
    "induce", "inducer", "induction", "inhibitor", "inhibition", "intron",
    "interaction", "isoform", "isoforms", "kinase", "kinesin", "knockdown",
    "knock-down", "knock-out", "knockout", "level", "ligand", "location",
    "locus", "lymphoma", "mammalian", "marker", "methilation", "modification",
    "moiety", "molecule", "molecules", "morpheein", "motif", "mrna", "mRNA",
    "mutant", "mutation", "mutations", "nonsynonymous", "non-synonymous",
    "nucleotide", "oligomerization", "oncoprotein", "overexpression",
    "over-expression", "pathway", "peptide", "pharmacokinetic",
    "pharmacodynamic", "pharmacogenetic" "phosphorylation", "polymorphism",
    "proliferation", "promoter", "protein", "protooncogene", "proto-oncogene",
    "pseudogene", "receptor", "receptors", "recruitment", "region",
    "regulator", "release", "repressor", "resistance", "retention",
    "ribonuclease", "rna", "role", "rrna", "sarcoma", "sequence", "sequences",
    "sequestration", "serum", "signaling", "sirnas", "sirna", "siRNA",
    "siRNAs", "SNP", "SNPs", "staining", "sumoylation", "synonymous", "targed",
    "T-cell", "transducer", "transgene", "translocation", "transcribe",
    "transcript", "transcription", "transporter", "tumor", "tumours", "tumour",
    "variant", "variation", "up-regulation", "upregulation", "vivo", "vitro"
    ])

# Snowball positive features
# NO LONGER USED
#snowball_pos_feats = frozenset([
#    "EXT_KEYWORD_MIN_[gene]@nn",
#    "EXT_KEYWORD_MIN_[gene]nn@",
#    "EXT_KEYWORD_MIN_[promoter]nn@",
#    "EXT_KEYWORD_MIN_[protein]nn@",
#    "EXT_KEYWORD_MIN_[protein]@nn",
#    "EXT_KEYWORD_MIN_[protein]nn@nn",
#    "EXT_KEYWORD_MIN_[protein]nsubj@",
#    "EXT_KEYWORD_MIN_[binding]prep_with@",
#    "EXT_KEYWORD_MIN_[mrna]nn@",
#    "EXT_KEYWORD_MIN_[activation]nn@",
#    "EXT_KEYWORD_MIN_[oligomerization]nn@",
#    "EXT_KEYWORD_MIN_[methylation]prep_of@",
#    "EXT_KEYWORD_MIN_[antibody]nn@",
#    "EXT_KEYWORD_MIN_[polymorphism]prep_of@",
#    "EXT_KEYWORD_MIN_[gene]appos@",
#    "EXT_KEYWORD_MIN_[enzyme]@nn",
#    "EXT_KEYWORD_MIN_[phosphorylation]prep_of@",
#    "EXT_KEYWORD_MIN_[receptor]@nn",
#    "EXT_KEYWORD_MIN_[histone]@nn",
#    "EXT_KEYWORD_MIN_[receptor]nn",
#    "IS_LONG_ALPHANUMERIC_MAIN_SYMBOL", "IS_HYPHENATED_SYMBOL", "IS_LONG_NAME"
#    ])

# Load the dictionaries that we need
merged_genes_dict = load_dict("merged_genes")
english_dict = load_dict("english")
stopwords_dict = load_dict("stopwords")
pos_mentions_dict = load_dict("pos_gene_mentions")
neg_mentions_dict = load_dict("neg_gene_mentions")
med_acrons_dict = load_dict("med_acrons")
long_names_dict = load_dict("long_names")
inverted_long_names = load_dict("inverted_long_names")

# Max mention length. We won't look at subsentences longer than this.
max_mention_length = 0
for key in merged_genes_dict:
    length = len(key.split())
    if length > max_mention_length:
        max_mention_length = length
# doubling to take into account commas and who knows what
max_mention_length *= 2

# Add features to a gene mention candidate
def add_features(mention, sentence):
    # The verb closest to the candidate, with the path to it.
    minl = 100
    minp = None
    minw = None
    for word in mention.words:
        for word2 in sentence.words:
            if word2.lemma.isalpha() and re.search('^VB[A-Z]*$', word2.pos) \
                    and word2.lemma != 'be':
                # Ignoring "be" comes from pharm (Emily)
                p = sentence.get_word_dep_path(word.in_sent_idx,
                                               word2.in_sent_idx)
                if len(p) < minl:
                    minl = len(p)
                    minp = p
                    minw = word2.lemma
    if minw:
        mention.add_feature('VERB_[' + minw + ']' + minp)
    # The keywords that appear in the sentence with the mention
    minl = 100
    minp = None
    minw = None
    for word in mention.words:
        for word2 in sentence.words:
            if word2.lemma in GENE_KEYWORDS:
                p = sentence.get_word_dep_path(
                    word.in_sent_idx, word2.in_sent_idx)
                if len(p) < minl:
                    minl = len(p)
                    minp = p
                    minw = word2.lemma
                if len(p) < 100:
                    mention.add_feature("KEYWORD_[" + word2.lemma + "]" + p)
    # Special features for the keyword on the shortest dependency path
    if minw:
        mention.add_feature('EXT_KEYWORD_MIN_[' + minw + ']' + minp)
        mention.add_feature('KEYWORD_MIN_[' + minw + ']')
    # If another gene is present in the sentence, add a feature with that gene
    # and the path to it. This comes from pharm.
    minl = 100
    minp = None
    minw = None
    for word in mention.words:
        for word2 in sentence.words:
            if word2 != word and word2.word in merged_genes_dict:
                p = sentence.get_word_dep_path(
                    word.in_sent_idx, word2.in_sent_idx)
                if len(p) < minl:
                    minl = len(p)
                    minp = p
                    minw = word2.lemma
    if minw:
        mention.add_feature('OTHER_GENE_['+minw+']' + minp)
        #mention.add_feature('OTHER_GENE_['+minw+']')
    # The lemma on the left of the candidate, whatever it is
    try:
        mention.add_feature(
            "NGRAM_LEFT_1_[" +
            sentence.words[mention.words[0].in_sent_idx-1].lemma + "]")
    except IndexError:
        pass
    # The lemma on the right of the candidate, whatever it is
    try:
        mention.add_feature(
            "NGRAM_RIGHT_1_[" +
            sentence.words[mention.words[-1].in_sent_idx+1].lemma + "]")
    except IndexError:
        pass
    # We know check whether the lemma on the left and on the right are
    # "special", for example a year or a gene.
    # The concept of left or right is a little tricky here, as we are actually
    # looking at the first word that contains only letters and is not a
    # stopword.
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
            gene_on_left = sentence.words[idx].word
        try:
            year = float(sentence.words[idx].word)
            if round(year) == year and year > 1950 and year <= 2014:
                mention.add_feature("IS_YEAR_LEFT")
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
            gene_on_right = sentence.words[idx].word
        try:
            year = float(sentence.words[idx].word)
            if round(year) == year and year > 1950 and year <= 2014:
                mention.add_feature("IS_YEAR_RIGHT")
        except:
            pass
    if gene_on_left and gene_on_right:
        mention.add_feature("IS_BETWEEN_GENES")
    elif gene_on_left:
        mention.add_feature("GENE_ON_LEFT")
    elif gene_on_right:
        mention.add_feature("GENE_ON_RIGHT")
    # The candidate is a single word that appears many times (more than 4) in
    # the sentence
    if len(mention.words) == 1 and \
            [w.word for w in sentence.words].count(mention.words[0].word) > 4:
        mention.add_feature("APPEARS_MANY_TIMES_IN_SENTENCE")
    # There are many PERSONs/ORGANIZATIONs/LOCATIONs in the sentence
    for ner in ["PERSON", "ORGANIZATION", "LOCATION"]:
        if [x.lemma for x in sentence.words].count(ner) > 4:
            mention.add_feature("MANY_{}_IN_SENTENCE".format(ner))
    # The candidate comes after an organization, or a location, or a person.
    # We skip commas as they may trick us.
    comes_after = None
    loc_idx = mention.wordidxs[0] - 1
    while loc_idx >= 0 and sentence.words[loc_idx].lemma == ",":
        loc_idx -= 1
    if loc_idx >= 0 and \
            sentence.words[loc_idx].ner in \
            ["ORGANIZATION", "LOCATION", "PERSON"] and \
            sentence.words[loc_idx].word not in merged_genes_dict:
        comes_after = sentence.words[loc_idx].ner
    # The candidate comes before an organization, or a location, or a person.
    # We skip commas, as they may trick us.
    comes_before = None
    loc_idx = mention.wordidxs[-1] + 1
    while loc_idx < len(sentence.words) and \
            sentence.words[loc_idx].lemma == ",":
        loc_idx += 1
    if loc_idx < len(sentence.words) and sentence.words[loc_idx].ner in \
            ["ORGANIZATION", "LOCATION", "PERSON"] and \
            sentence.words[loc_idx].word not in merged_genes_dict:
        comes_before = sentence.words[loc_idx].ner
    # All the following is commented out because it's not a context feature
    # The following features deal with the "appearance" of the symbol.
    # They are _not_ context features, but they are reasonable.
    # If it looks like a duck, it quacks like a duck, and it flies like a duck,
    # then it's probably a duck.
    # All the following features are added only if the candidate is a single
    # word.
    #if len(mention.words) == 1:
    #    entity_is_word = False
    #    entity_in_dict = False
    #    for entity in mention.entity.split("|"):
    #        if entity == mention.words[0].word:
    #            entity_is_word = True
    #        if entity in merged_genes_dict:
    #            entity_in_dict = True
    #    if entity_is_word and entity_in_dict and \
    #            (comes_before is None or comes_after is None):
    #        # The mention is a 'main' symbol
    #        if mention.words[0].word.isalnum() and \
    #                not mention.words[0].word.isalpha():
    #            if len(mention.words[0].word) >= 4:
    #                mention.add_feature("IS_LONG_ALPHANUMERIC_MAIN_SYMBOL")
    #            else:
    #                is_letter_plus_number = False
    #                try:
    #                    int(mention.words[0].word[1:])
    #                    is_letter_plus_number = True
    #                except:
    #                    is_letter_plus_number = False
    #                if is_letter_plus_number:
    #                    mention.add_feature(
    #                        "IS_LETTER_NUMBER_MAIN_SYMBOL_[{}]".format(
    #                            mention.words[0].word))
    #                else:
    #                    mention.add_feature(
    #                        "IS_SHORT_ALPHANUMERIC_MAIN_SYMBOL_[{}]".format(
    #                            mention.words[0].word))
    #        elif len(mention.words[0].word) >= 4:
    #            mention.add_feature("IS_LONG_MAIN_SYMBOL_[{}]".format(
    #                mention.words[0].word))
    #    elif entity_in_dict or mention.words[0].word in merged_genes_dict:
    #        if len(mention.words[0].word) > 3 and \
    #                mention.words[0].word.casefold() == mention.words[0].word \
    #                and not re.match("^p[0-9]+$", mention.words[0].word):
    #            # Long name - We supervise these.
    #            #mention.add_feature("IS_LONG_NAME")
    #            pass
    #        elif mention.words[0].word in inverted_long_names:
    #            # Long name - We supervise these
    #            #mention.add_feature("IS_LONG_NAME")
    #            pass
    #        elif "-" in mention.words[0].word and comes_after != "PERSON":
    #            mention.add_feature("IS_HYPHENATED_SYMBOL")
    #        elif mention.words[0].word.casefold().endswith("alpha") or \
    #                mention.words[0].word.casefold().endswith("beta") or \
    #                mention.words[0].word.casefold().endswith("gamma"):
    #            mention.add_feature("ENDS_WITH_GREEK")
    #        elif re.match("^p[0-9][0-9]$", mention.words[0].word):
    #            mention.add_feature("IS_PXX_SYMBOL_[{}]".format(
    #                mention.words[0].word))
    #        elif mention.words[0].word.isalnum() and \
    #                not mention.words[0].word.isalpha():
    #            if len(mention.words[0].word) >= 4:
    #                mention.add_feature(
    #                    "IS_LONG_ALPHANUMERIC_ALTERN_SYMBOL_[{}]".format(
    #                        mention.words[0].word))
    #        elif len(mention.words[0].word) >= 4:
    #            mention.add_feature("IS_LONG_ALTERN_SYMBOL_[{}]".format(
    #                mention.words[0].word))


# Supervise the candidates.
# For each mention we supervise we create one (or more) supervised copies,
# possibly with different features
def supervise(mentions, sentence, acronyms, acro_defs):
    phrase = " ".join([x.word for x in sentence.words])
    new_mentions = []
    for mention in mentions:
        new_mentions.append(mention)
        # The candidate is a long name.
        if " ".join([word.word for word in mention.words]) in \
                inverted_long_names:
            supervised = Mention("GENE_SUP_long", mention.entity,
                                 mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = True
            new_mentions.append(supervised)
            continue
        # The phrase starts with words that are indicative of the candidate not
        # being a mention of a gene
        # We add a feature for this, as it is a context property
        if phrase.startswith("Performed the experiments :") or \
                phrase.startswith("Wrote the paper :") or \
                phrase.startswith("W'rote the paper :") or \
                phrase.startswith("Wlrote the paper") or \
                phrase.startswith("Contributed reagents") or \
                phrase.startswith("Analyzed the data :") or \
                phrase.casefold().startswith("address"):
            supervised = Mention("GENE_SUP_contr", mention.entity, mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = False
            new_mentions.append(supervised)
            # This copy only contains the "special" feature
            supervised2 = Mention("GENE_SUP_contr2", mention.entity, mention.words)
            supervised2.is_correct = False
            supervised2.add_feature("IN_CONTRIB_PHRASE")
            new_mentions.append(supervised2)
            # Add the "special feature to the original mention
            mention.add_feature("IN_CONTRIB_PHRASE")
            continue
        # The candidate is an entry in Gene Ontology
        if len(mention.words) == 1 and mention.words[0].word == "GO":
            try:
                if sentence.words[mention.words[0].in_sent_idx + 1][0] == ":":
                    supervised = Mention("GENE_SUP_go", mention.entity,
                                         mention.words)
                    supervised.features = mention.features.copy()
                    supervised.is_correct = False
                    new_mentions.append(supervised)
            except:
                pass
            continue
        # Index of the word on the left
        idx = mention.wordidxs[0] - 1
        if idx >= 0:
            # The candidate is preceded by a "%" (it's probably a quantity)
            if sentence.words[idx].word == "%":
                supervised = Mention("GENE_SUP_%", mention.entity,
                                     mention.words)
                supervised.features = mention.features.copy()
                supervised.is_correct = False
                new_mentions.append(supervised)
                continue
            # The candidate comes after a "document element" (e.g., table, or
            # figure)
            if sentence.words[idx].word.casefold() in DOC_ELEMENTS:
                supervised = Mention("GENE_SUP_doc", mention.entity, mention.words)
                supervised.features = mention.features.copy()
                supervised.is_correct = False
                new_mentions.append(supervised)
                continue
            # The candidate comes after an "individual" word (e.g.,
            # "individual")
            if sentence.words[idx].word.casefold() in INDIVIDUALS and \
                    not mention.words[0].word.isalpha() and \
                    not len(mention.words[0].word) > 4:
                supervised = Mention("GENE_SUP_indiv", mention.entity, mention.words)
                supervised.features = mention.features.copy()
                supervised.is_correct = False
                new_mentions.append(supervised)
                continue
            # The candidate comes after a "type" word, and it is made only of
            # the letters "I" and "V"
            if sentence.words[idx].lemma.casefold() in TYPES and \
                    set(mention.words[0].word).issubset(set(["I", "V"])):
                supervised = Mention("GENE_SUP_type", mention.entity, mention.words)
                supervised.features = mention.features.copy()
                supervised.is_correct = False
                new_mentions.append(supervised)
                continue
        # Index of the word on the right
        idx = mention.wordidxs[-1] + 1
        if idx < len(sentence.words):
            # The candidate is followed by a "=" (it's probably a quantity)
            if sentence.words[idx].word == "=":
                supervised = Mention("GENE_SUP_=", mention.entity,
                                     mention.words)
                supervised.features = mention.features.copy()
                supervised.is_correct = False
                new_mentions.append(supervised)
                continue
            # The candidate is followed by a ":" and the word after it is a
            # number (it's probably a quantity)
            if sentence.words[idx].word == ":":
                try:
                    float(sentence.words[idx + 1].word)
                    supervised = Mention("GENE_SUP_:", mention.entity,
                                         mention.words)
                    supervised.features = mention.features.copy()
                    supervised.is_correct = False
                    new_mentions.append(supervised)
                except:  # both ValueError and IndexError
                    pass
                continue
            # The candidate comes before "et"
            if sentence.words[idx].word == "et":
                supervised = Mention("GENE_SUP_et", mention.entity, mention.words)
                supervised.features = mention.features.copy()
                supervised.is_correct = False
                new_mentions.append(supervised)
                continue
        # The candidate is a DNA triplet
        # We check this by looking at whether the word before or after is also
        # a DNA triplet.
        if len(mention.words) == 1 and len(mention.words[0].word) == 3 and \
                set(mention.words[0].word) <= set("ACGT"):
            done = False
            idx = mention.wordidxs[0] - 1
            if idx > 0:
                if set(sentence.words[idx].word) <= set("ACGT"):
                    supervised = Mention("GENE_SUP_dna", mention.entity,
                                         mention.words)
                    supervised.features = mention.features.copy()
                    supervised.is_correct = False
                    new_mentions.append(supervised)
                    continue
            idx = mention.wordidxs[-1] + 1
            if not done and idx < len(sentence.words):
                if set(sentence.words[idx].word) <= set("ACGT"):
                    supervised = Mention("GENE_SUP_dna", mention.entity,
                                         mention.words)
                    supervised.features = mention.features.copy()
                    supervised.is_correct = False
                    new_mentions.append(supervised)
                    continue
        # If it's "II", it's most probably wrong.
        if mention.words[0].word == "II":
            supervised = Mention("GENE_SUP_ii", mention.entity,
                                 mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = False
            new_mentions.append(supervised)
            continue
        # Snowball positive features
        # Commented out to avoid overfitting
        #if mention.features & snowball_pos_feats:
        #    supervised = Mention("GENE_SUP", mention.entity,
        #                         mention.words)
        #    supervised.features = mention.features - snowball_pos_feats
        #    supervised.is_correct = True
        #    new_mentions.append(supervised)
        #    supervised2 = Mention("GENE_SUP", mention.entity,
        #                          mention.words)
        #    supervised2.features = mention.features & snowball_pos_feats
        #    supervised2.is_correct = True
        #    new_mentions.append(supervised2)
        #    continue
        ## Some negative features
        #if "EXT_KEYWORD_MIN_[chromosome]@nn" in mention.features:
        #    supervised = Mention("GENE_SUP", mention.entity, mention.words)
        #    supervised.features = mention.features.copy()
        #    supervised.is_correct = False
        #    new_mentions.append(supervised)
        #    continue
        #if "IS_YEAR_RIGHT" in mention.features:
        #    supervised = Mention("GENE_SUP", mention.entity, mention.words)
        #    supervised.features = mention.features.copy()
        #    supervised.is_correct = False
        #    new_mentions.append(supervised)
        #    continue
        # The candidate comes after an organization, or a location, or a person.
        # We skip commas as they may trick us.
        comes_after = None
        loc_idx = mention.wordidxs[0] - 1
        while loc_idx >= 0 and sentence.words[loc_idx].lemma == ",":
            loc_idx -= 1
        if loc_idx >= 0 and \
                sentence.words[loc_idx].ner in \
                ["ORGANIZATION", "LOCATION", "PERSON"] and \
                sentence.words[loc_idx].word not in merged_genes_dict:
            comes_after = sentence.words[loc_idx].ner
        # The candidate comes before an organization, or a location, or a person.
        # We skip commas, as they may trick us.
        comes_before = None
        loc_idx = mention.wordidxs[-1] + 1
        while loc_idx < len(sentence.words) and \
                sentence.words[loc_idx].lemma == ",":
            loc_idx += 1
        if loc_idx < len(sentence.words) and sentence.words[loc_idx].ner in \
                ["ORGANIZATION", "LOCATION", "PERSON"] and \
                sentence.words[loc_idx].word not in merged_genes_dict:
            comes_before = sentence.words[loc_idx].ner
        # Not correct if it's most probably a person name.
        if comes_before and comes_after:
            supervised = Mention("GENE_SUP_name", mention.entity, mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = False
            new_mentions.append(supervised)
            continue
        # Comes after person and before "," or ":", so it's probably a person
        # name
        if comes_after == "PERSON" and \
                mention.words[-1].in_sent_idx + 1 < len(sentence.words) and \
                sentence.words[mention.words[-1].in_sent_idx + 1].word \
                in [",", ":"]:
            supervised = Mention("GENE_SUP_name2", mention.entity, mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = False
            new_mentions.append(supervised)
            continue
        if comes_after == "PERSON" and mention.words[0].ner == "PERSON":
            supervised = Mention("GENE_SUP_name3", mention.entity, mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = False
            new_mentions.append(supervised)
            continue
        # Is a location and comes before a location so it's probably wrong
        if comes_before == "LOCATION" and mention.words[0].ner == "LOCATION":
            supervised = Mention("GENE_SUP_loc", mention.entity, mention.words)
            supervised.features = mention.features.copy()
            supervised.is_correct = False
            new_mentions.append(supervised)
            continue
        # Handle acronyms
        if acro_defs and  \
                " ".join([word.word for word in mention.words]) not in \
                inverted_long_names:
            # Only process as acronym if that's the case
            if mention.words[0].word in acronyms:
                contains_kw = False
                try:
                    defs = acro_defs[mention.words[0].word]
                except:
                    continue
                for definition in defs:
                    # If the definition is in the gene dictionary, supervise as
                    # correct
                    if definition in merged_genes_dict:
                        if not (comes_before and comes_after):
                            supervised = Mention("GENE_SUP_acr_t",
                                    mention.entity, mention.words)
                            supervised.features = mention.features.copy()
                            supervised.is_correct = True
                            new_mentions.append(supervised)
                            break
                    else:
                        # Check if the definition contains some keywords that
                        # make us suspect that it is probably a gene/protein
                        # This list is incomplete, and it would be good to add
                        # to it.
                        definition = definition.casefold()
                        if contains_kw:
                            continue
                        for word in definition.split():
                            if word.endswith("ase") and word != "phase":
                                contains_kw = True
                                break
                        if " gene" in definition or "protein" in definition \
                                or "factor" in  definition or \
                                "ligand" in definition or \
                                "kinase" in definition or \
                                "enzyme" in definition or \
                                "receptor" in definition or \
                                "decarboxylase" in definition or \
                                "pseudogene" in definition:
                            contains_kw = True
                        # If no significant keyword, supervise as not correct
                        if not contains_kw:
                            supervised = Mention("GENE_SUP_acr_f", 
                                    mention.entity, mention.words)
                            supervised.features = mention.features.copy()
                            supervised.is_correct = False
                            new_mentions.append(supervised)
                            break
    return new_mentions


# Return a list of mention candidates extracted from the sentence
def extract(sentence):
    mentions = []
    # Skip the sentence if there are no English words in the sentence
    no_english_words = True
    for word in sentence.words:
        if len(word.word) > 2 and \
                (word.word in english_dict or
                 word.word.casefold() in english_dict):
            no_english_words = False
            break
    if no_english_words:
        return []  # Stop iteration

    sentence_is_upper = False
    if " ".join([x.word for x in sentence.words]).isupper():
        sentence_is_upper = True
    # The following set keeps a list of indexes we already looked at and which
    # contained a mention
    history = set()
    words = sentence.words
    # Scan all subsequences of the sentence of length up to max_mention_length
    for start, end in get_all_phrases_in_sentence(sentence,
                                                  max_mention_length):
        if start in history or end in history:
                continue
        phrase = " ".join([word.word for word in words[start:end]])
        if sentence_is_upper:  # This may not be a great idea...
            phrase = phrase.casefold()
        mention = None
        # If the phrase is in the dictionary, then is a mention candidate
        if len(phrase) > 1 and phrase in merged_genes_dict:
            # The entity is a list of all the main symbols that could have the
            # phrase as symbol. They're separated by "|".
            mention = Mention("GENE",
                              "|".join(merged_genes_dict[phrase]),
                              words[start:end])
            # Add features to the candidate
            add_features(mention, sentence)
            # Add mention to the list
            mentions.append(mention)
            # Add indexes to history so that they are not used for another
            # mention
            for i in range(start, end):
                history.add(i)
    return mentions


if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "bounding_boxes", "acronyms", "definitions"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list, TSVstring2list, TSVstring2dict])
            # Create the sentence object
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
            else:
                line_dict["acronyms"] = None
                line_dict["definitions"] = None
            # Get list of mentions candidates in this sentence
            mentions = extract(sentence)
            # Supervise them
            new_mentions = supervise(
                mentions, sentence, line_dict["acronyms"],
                line_dict["definitions"])
            # Print!
            for mention in new_mentions:
                print(mention.tsv_dump())
