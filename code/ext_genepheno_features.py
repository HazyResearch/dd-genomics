#! /usr/bin/env python3

import fileinput
import re

from dstruct.Sentence import Sentence
from helper.easierlife import get_dict_from_TSVline, TSVstring2list, no_op, \
    print_feature


# Add features
def add_features(relation_id, gene_words, pheno_words, sentence):
    # Find the start/end indices of the mentions composing the relation
    gene_start = gene_words[0].in_sent_idx
    pheno_start = pheno_words[0].in_sent_idx
    gene_end = gene_words[-1].in_sent_idx
    pheno_end = pheno_words[-1].in_sent_idx
    limits = sorted((gene_start, pheno_start, gene_end, pheno_end))
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
    verbs_between = []
    minl_gene = 100
    minp_gene = None
    minw_gene = None
    mini_gene = None
    minl_pheno = 100
    # minp_pheno = None
    minw_pheno = None
    mini_pheno = None
    neg_found = False
    # Look all the words, as in the dependency path there could be words that
    # are close to both mentions but not between them
    for i in range(len(sentence.words)):
        # The filtering of the brackets and commas is from Emily's code.
        if re.search('^VB[A-Z]*$', sentence.words[i].pos) and \
                sentence.words[i].word not in ["{", "}", "(", ")", "[", "]"] \
                and "," not in sentence.words[i].word:
            (p_gene, l_gene) = sentence.get_word_dep_path(
                betw_start, sentence.words[i].in_sent_idx)
            (p_pheno, l_pheno) = sentence.get_word_dep_path(
                sentence.words[i].in_sent_idx, betw_end)
            if l_gene < minl_gene:
                minl_gene = l_gene
                minp_gene = p_gene
                minw_gene = sentence.words[i].lemma
                mini_gene = sentence.words[i].in_sent_idx
            if l_pheno < minl_pheno:
                minl_pheno = l_pheno
                #  minp_pheno = p_pheno
                minw_pheno = sentence.words[i].lemma
                mini_pheno = sentence.words[i].in_sent_idx
            # Look for negation.
            if i > 0 and sentence.words[i-1].lemma in \
                    ["no", "not", "neither", "nor"]:
                if i < betw_end - 2:
                    neg_found = True
                    print_feature(
                        relation_id,
                        inv + "NEG_VERB_[" + sentence.words[i-1].word + "]-" +
                        sentence.words[i].lemma)
            else:
                verbs_between.append(sentence.words[i])
    if len(verbs_between) == 1 and not neg_found:
        print_feature(
            sentence.doc_id, relation_id,
            inv + "SINGLE_VERB_[%s]" % verbs_between[0].lemma)
    else:
        for verb in verbs_between:
            if verb.in_sent_idx > betw_start and \
                    verb.in_sent_idx < betw_end:
                print_feature(
                    sentence.doc_id, relation_id,
                    inv + "VERB_[%s]" % verb.lemma)
    if mini_pheno == mini_gene and mini_gene is not None and \
            len(minp_gene) < 50:  # and "," not in minw_gene:
        # feature = inv + 'MIN_VERB_[' + minw_gene + ']' + minp_gene
        # features.append(feature)
        feature = inv + 'MIN_VERB_[' + minw_gene + ']'
        print_feature(sentence.doc_id, relation_id, feature)
    else:
        feature = inv
        if mini_gene is not None:
            # feature = 'MIN_VERB_GENE_[' + minw_gene + ']' + minp_gene
            # print_feature(sentence.doc_id, relation_id, feature)
            feature += 'MIN_VERB_GENE_[' + minw_gene + ']'
        else:
            feature += 'MIN_VERB_GENE_[NULL]'
        if mini_pheno is not None:
            # feature = 'MIN_VERB_pheno_[' + minw_pheno + ']' + minp_pheno)
            # print_feature(sentence.doc_id, relation_id, feature)
            feature += '_pheno_[' + minw_pheno + ']'
        else:
            feature += '_pheno_[NULL]'
        print_feature(sentence.doc_id, relation_id, feature)

    # The following features are only added if the two mentions are "close
    # enough" to avoid overfitting. The concept of "close enough" is somewhat
    # arbitrary.
    neg_word_index = -1
    if betw_end - betw_start - 1 < 8:
        for i in range(betw_start+1, betw_end):
            # Feature for separation between entities.
            # TODO Think about merging these?
            # I think these should be some kind of supervision rule instead?
            if "while" == sentence.words[i].lemma:
                print_feature(sentence.doc_id, relation_id, "SEP_BY_[while]")
            if "whereas" == sentence.words[i].lemma:
                print_feature(sentence.doc_id, relation_id, "SEP_BY_[whereas]")
            if sentence.words[i].lemma in ["no", "not", "neither", "nor"]:
                neg_word_index = i
        # Features for the negative words
        # TODO: We would probably need distant supervision for these
        if neg_word_index > -1:
            gene_p = None
            gene_l = 100
            for word in sentence.words[gene_start:gene_end+1]:
                (p, l) = sentence.get_word_dep_path(
                    word.in_sent_idx, neg_word_index)
                if l < gene_l:
                    gene_p = p
                    gene_l = l
            if gene_p:
                print_feature(
                    sentence.doc_id, relation_id, inv + "NEG_[" + gene_p + "]")
            # pheno_p = None
            # pheno_l = 100
            # for word in sentence.words[pheno_start:pheno_end+1]:
            #    p = sentence.get_word_dep_path(
            #        word.in_sent_idx, neg_word_index)
            #    if len(p) < pheno_l:
            #        pheno_p = p
            #        pheno_l = len(p)
            # if pheno_p:
            #    print_feature(
            #       relation_id, inv + "pheno_TO_NEG_[" + pheno_p + "]")
        # The sequence of lemmas between the two mentions and the sequence of
        # lemmas between the two mentions but using the NERs, if present, and
        # the sequence of POSes between the mentions
        seq_list_ners = []
        seq_list_lemmas = []
        seq_list_poses = []
        for word in sentence.words[betw_start+1:betw_end]:
            if word.ner != "O":
                seq_list_ners.append(word.ner)
            else:
                seq_list_ners.append(word.lemma)
            seq_list_lemmas.append(word.lemma)
            seq_list_poses.append(word.pos)
        seq_ners = " ".join(seq_list_ners)
        seq_lemmas = " ".join(seq_list_lemmas)
        seq_poses = "_".join(seq_list_poses)
        print_feature(
            sentence.doc_id, relation_id,
            inv + "WORD_SEQ_[" + seq_lemmas + "]")
        print_feature(
            sentence.doc_id, relation_id,
            inv + "WORD_SEQ_NER_[" + seq_ners + "]")
        print_feature(
            sentence.doc_id, relation_id, inv + "POS_SEQ_[" + seq_poses + "]")
        # Shortest dependency path between the two mentions
        (path, length) = sentence.dep_path(gene_words, pheno_words)
        print_feature(
            sentence.doc_id, relation_id, inv + "DEP_PATH_[" + path + "]")
    # Number of words between the mentions
    # TODO I think this should be some kind of supervision rule instead?
    # print_feature(sentence.doc_id, relation_id,
    #    inv + "WORD_SEQ_LEN_[" + str(betw_end - betw_start - 1) + "]")
    # 2-gram between the mentions
    if betw_end - betw_start - 1 > 4 and betw_start - betw_end - 1 < 15:
        for i in range(betw_start + 1, betw_end - 1):
            print_feature(
                sentence.doc_id, relation_id,
                "BETW_2_GRAM_[" + sentence.words[i].lemma + "_" +
                sentence.words[i+1].lemma + "]")
    # Lemmas on the exterior of the mentions and on the interior
    feature = inv
    if start > 0:
        feature += "EXT_NGRAM_[" + sentence.words[start - 1].lemma + "]"
    else:
        feature += "EXT_NGRAM_[NULL]"
    if end < len(sentence.words) - 1:
        feature += "_[" + sentence.words[end + 1].lemma + "]"
    else:
        feature += "_[NULL]"
    print_feature(sentence.doc_id, relation_id, feature)
    feature = inv + "INT_NGRAM_[" + sentence.words[betw_start + 1].lemma + \
        "]" + "_[" + sentence.words[betw_end - 1].lemma + "]"
    print_feature(sentence.doc_id, relation_id, feature)


if __name__ == "__main__":
    # Process the input
    with fileinput.input() as input_files:
        for line in input_files:
            # Parse the TSV line
            line_dict = get_dict_from_TSVline(
                line, ["doc_id", "sent_id", "wordidxs", "words", "poses",
                       "ners", "lemmas", "dep_paths", "dep_parents",
                       "relation_id", "gene_wordidxs", "pheno_wordidxs"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                    TSVstring2list, TSVstring2list, TSVstring2list,
                    TSVstring2list, lambda x: TSVstring2list(x, int),
                    no_op, lambda x: TSVstring2list(x, int), lambda x:
                    TSVstring2list(x, int)])
            # Create the sentence object
            null_list = [None, ] * len(line_dict["wordidxs"])
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], null_list)
            if sentence.is_weird():
                continue
            gene_words = []
            for gene_wordidx in line_dict["gene_wordidxs"]:
                gene_words.append(sentence.words[gene_wordidx])
            pheno_words = []
            for pheno_wordidx in line_dict["pheno_wordidxs"]:
                pheno_words.append(sentence.words[pheno_wordidx])
            add_features(
                line_dict["relation_id"], gene_words, pheno_words, sentence)
