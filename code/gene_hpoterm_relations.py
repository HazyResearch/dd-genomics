#! /usr/bin/env python3

import fileinput
import re

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2bool, \
    TSVstring2list


# Add features
def add_features(relation, gene_mention, hpoterm_mention, sentence):
    # Find the start/end indices of the mentions composing the relation
    gene_start = gene_mention.wordidxs[0]
    hpoterm_start = hpoterm_mention.wordidxs[0]
    gene_end = gene_mention.wordidxs[-1]
    hpoterm_end = hpoterm_mention.wordidxs[-1]
    limits = sorted((gene_start, hpoterm_start, gene_end, hpoterm_end))
    start = limits[0]
    betw_start = limits[1]
    betw_end = limits[2]
    end = limits[3]
    # If the gene comes first, we do not prefix, otherwise we do.
    if start == gene_start:
        inv = ""
    else:
        inv = "INV_"

    # Verbs between the mentions
    # A lot of this comes from Emily's code
    ws = []
    verbs_between = []
    minl_gene = 100
    minp_gene = None
    minw_gene = None
    mini_gene = None
    minl_hpo = 100
    minp_hpo = None
    minw_hpo = None
    mini_hpo = None
    neg_found = False
    # Emily's code was only looking at the words between the mentions, but it
    # is more correct (in my opinion) to look all the words, as in the
    # dependency path there could be words that are close to both mentions but
    # not between them
    #for i in range(betw_start+1, betw_end):
    for i in range(len(sentence.words)):
        if "," not in sentence.words[i].lemma:
            ws.append(sentence.words[i].lemma)
            # Feature for separation between entities
            # TODO Think about merging these?
            if "while" == sentence.words[i].lemma:
                relation.add_feature("SEP_BY_[while]")
            if "whereas" == sentence.words[i].lemma:
                relation.add_feature("SEP_BY_[whereas]")
        # The filtering of the brackets and commas is from Emily's code. I'm
        # not sure it is actually needed, but it won't hurt.
        if re.search('^VB[A-Z]*', sentence.words[i].pos) and \
                sentence.words[i].word != "{" and \
                sentence.words[i].word != "}" and \
                "," not in sentence.words[i].word:
            p_gene = sentence.get_word_dep_path(betw_start,
                    sentence.words[i].in_sent_idx)
            p_hpo = sentence.get_word_dep_path(
                    sentence.words[i].in_sent_idx, betw_end)
            if len(p_gene) < minl_gene:
                minl_gene = len(p_gene)
                minp_gene = p_gene
                minw_gene = sentence.words[i].lemma
                mini_gene = sentence.words[i].in_sent_idx
            if len(p_hpo) < minl_hpo:
                minl_hpo = len(p_hpo)
                minp_hpo = p_hpo
                minw_hpo = sentence.words[i].lemma
                mini_hpo = sentence.words[i].in_sent_idx
            # Look for negation.
            if i > 0:
                if sentence.words[i-1].lemma in ["no", "not", "neither", "nor"]:
                    if i < betw_end - 2:
                        neg_found = True
                        relation.add_feature(inv + "NEG_VERB_[" +
                                sentence.words[i-1].word + "]-" +
                                sentence.words[i].lemma)
                elif sentence.words[i] != "{" and sentence.words[i] != "}":
                    verbs_between.append(sentence.words[i].lemma)
    if len(verbs_between) == 1 and not neg_found:
        relation.add_feature(inv + "SINGLE_VERB_[%s]" % verbs_between[0])
    else:
        for verb in verbs_between:
            relation.add_feature(inv + "VERB_[%s]" % verb)
    if mini_hpo == mini_gene and mini_gene != None and len(minp_gene) < 50: # and "," not in minw_gene:
        # feature = inv + 'MIN_VERB_[' + minw_gene + ']' + minp_gene
        # features.append(feature)
        feature = inv + 'MIN_VERB_[' + minw_gene + ']'
        relation.add_feature(feature)
    else:
        if mini_gene != None:
            # feature = 'MIN_VERB_GENE_[' + minw_gene + ']' + minp_gene
            # relation.add_feature(feature)
            feature = inv + 'MIN_VERB_GENE_[' + minw_gene + ']'
            relation.add_feature(feature)
        if mini_hpo != None:
            # feature = 'MIN_VERB_HPO_[' + minw_hpo + ']' + minp_hpo)
            # relation.add_feature(feature)
            feature = inv + 'MIN_VERB_HPO_[' + minw_hpo + ']'
            relation.add_feature(feature)
    # Shortest dependency path between the two mentions
    relation.add_feature(inv + "DEP_PATH_[" + sentence.dep_path(gene_mention,
        hpoterm_mention) + "]")
    # The sequence of lemmas between the two mentions
    if len(ws) < 7 and len(ws) > 0 and "{" not in ws and "}" not in ws and \
            "\"" not in ws and "/" not in ws and "\\" not in ws and \
            "," not in ws and \
            " ".join(ws) not in ["_ and _", "and", "or",  "_ or _"]:
            relation.add_feature(inv + "WORD_SEQ_[%s]" % " ".join(ws))
    # Number of words between the mentions
    relation.add_feature(inv + "WORD_SEQ_LEN_[%d]" % len(ws))
    # The sequence of lemmas between the two mentions but using the NERs, if
    # present
    seq_list = []
    for word in sentence.words[betw_start+1:betw_end]:
        if word.ner != "O":
            seq_list.append(word.ner)
        else:
            seq_list.append(word.lemma)
    seq = "_".join(seq_list)
    relation.add_feature(inv + "WORD_SEQ_NER_[" + seq + "]")
    # Lemmas on the left and on the right
    if gene_start > 0:
        relation.add_feature("GENE_NGRAM_LEFT_1_[" +
            sentence.words[gene_start-1].lemma + "]")
    if gene_end < len(sentence.words) - 1:
        relation.add_feature("GENE_NGRAM_RIGHT_1_[" +
            sentence.words[gene_end+1].lemma + "]")
    if hpoterm_start > 0:
        relation.add_feature("HPO_NGRAM_LEFT_1_[" +
            sentence.words[hpoterm_start-1].lemma + "]")
    if hpoterm_end < len(sentence.words) - 1:
        relation.add_feature("HPO_NGRAM_RIGHT_1_[" +
            sentence.words[hpoterm_end+1].lemma + "]")


# Load the gene<->hpoterm dictionary
genehpoterms_dict = load_dict("genehpoterms")

if __name__ == "__main__":
    # Process input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "bounding_boxes", "gene_entity", "gene_wordidxs",
                       "gene_is_correct", "gene_type",
                       "hpoterm_entity", "hpoterm_wordidxs",
                       "hpoterm_is_correct", "hpoterm_type"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    TSVstring2list, no_op, lambda x: TSVstring2list(x, int),
                    TSVstring2bool, no_op, no_op, lambda x: TSVstring2list(x,
                    int), TSVstring2bool, no_op])
            # Create the sentence object where the two mentions appear
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Create the mentions
            gene_mention = Mention(
                "GENE", line_dict["gene_entity"],
                [sentence.words[j] for j in line_dict["gene_wordidxs"]])
            gene_mention.is_correct = line_dict["gene_is_correct"]
            gene_mention.type = line_dict["gene_type"]
            hpoterm_mention = Mention(
                "HPOTERM", line_dict["hpoterm_entity"],
                [sentence.words[j] for j in line_dict["hpoterm_wordidxs"]])
            hpoterm_mention.is_correct = line_dict["hpoterm_is_correct"]
            hpoterm_mention.type = line_dict["hpoterm_type"]
            # If the word indexes do not overlap, create the relation candidate
            if not set(line_dict["gene_wordidxs"]) & \
                    set(line_dict["hpoterm_wordidxs"]):
                relation = Relation(
                    "GENEHPOTERM", gene_mention, hpoterm_mention)
                # Add features
                add_features(relation, gene_mention, hpoterm_mention,
                            sentence)
                # Supervise
                # One of the two mentions is labelled as False
                # We do not create a copy in this case because there will
                # already be an unsupervised copy built on the unsupervised
                # copies of the mentions.
                if gene_mention.is_correct is False or \
                        hpoterm_mention.is_correct is False:
                    relation.is_correct = False
                    relation.type = "GENEHPOTERM_SUP_F"
                # Present in the existing HPO mapping and not a candidate built
                # on top of the unsupervised copies of false-supervised
                # gene/hpoterm mentions (either or both).
                elif not gene_mention.type.endswith("_ORIG_F") and not \
                        hpoterm_mention.type.endswith("_ORIG_F"):
                    in_mapping = False
                    hpo_entity_id = hpoterm_mention.entity.split("|")[0]
                    for gene in gene_mention.entity.split("|"):
                        if frozenset([gene, hpo_entity_id]) in genehpoterms_dict:
                            in_mapping = True
                    if frozenset([gene_mention.words[0].word, hpo_entity_id]) in \
                            genehpoterms_dict:
                        in_mapping = True
                    if in_mapping:
                        supervised = Relation(
                            "GENEHPOTERM_SUP_MAP", gene_mention, hpoterm_mention)
                        supervised.features = relation.features
                        supervised.is_correct = True
                        print(supervised.tsv_dump())
                        relation.type = "GENEHPOTERM_ORIG_T"
                # Print!
                print(relation.tsv_dump())
