#! /usr/bin/env python3

import fileinput
import re

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2list


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
    # If the gene comes first, we do not prefix, otherwise we do.
    if start == gene_start:
        inv = ""
    else:
        inv = "INV_"

    # Verbs between the mentions
    # A lot of this comes from Emily's code
    verbs_between = []
    minl_gene = 100
    minp_gene = None
    minw_gene = None
    mini_gene = None
    minl_hpo = 100
    # minp_hpo = None
    minw_hpo = None
    mini_hpo = None
    neg_found = False
    # Emily's code was only looking at the words between the mentions, but it
    # is more correct (in my opinion) to look all the words, as in the
    # dependency path there could be words that are close to both mentions but
    # not between them
    for i in range(len(sentence.words)):
        # The filtering of the brackets and commas is from Emily's code. I'm
        # not sure it is actually needed, but it won't hurt.
        if re.search('^VB[A-Z]*$', sentence.words[i].pos) and \
                sentence.words[i].word != "{" and \
                sentence.words[i].word != "}" and \
                "," not in sentence.words[i].word:
            p_gene = sentence.get_word_dep_path(
                betw_start, sentence.words[i].in_sent_idx)
            p_hpo = sentence.get_word_dep_path(
                sentence.words[i].in_sent_idx, betw_end)
            if len(p_gene) < minl_gene:
                minl_gene = len(p_gene)
                minp_gene = p_gene
                minw_gene = sentence.words[i].lemma
                mini_gene = sentence.words[i].in_sent_idx
            if len(p_hpo) < minl_hpo:
                minl_hpo = len(p_hpo)
                #  minp_hpo = p_hpo
                minw_hpo = sentence.words[i].lemma
                mini_hpo = sentence.words[i].in_sent_idx
            # Look for negation.
            if i > 0:
                if sentence.words[i-1].lemma in \
                        ["no", "not", "neither", "nor"]:
                    if i < betw_end - 2:
                        neg_found = True
                        relation.add_feature(
                            inv + "NEG_VERB_[" +
                            sentence.words[i-1].word + "]-" +
                            sentence.words[i].lemma)
                elif sentence.words[i] != "{" and sentence.words[i] != "}":
                    verbs_between.append(sentence.words[i].lemma)
    if len(verbs_between) == 1 and not neg_found:
        relation.add_feature(inv + "SINGLE_VERB_[%s]" % verbs_between[0])
    else:
        for verb in verbs_between:
            relation.add_feature(inv + "VERB_[%s]" % verb)
    if mini_hpo == mini_gene and mini_gene is not None and \
            len(minp_gene) < 50:  # and "," not in minw_gene:
        # feature = inv + 'MIN_VERB_[' + minw_gene + ']' + minp_gene
        # features.append(feature)
        feature = inv + 'MIN_VERB_[' + minw_gene + ']'
        relation.add_feature(feature)
    else:
        if mini_gene is not None:
            # feature = 'MIN_VERB_GENE_[' + minw_gene + ']' + minp_gene
            # relation.add_feature(feature)
            feature = inv + 'MIN_VERB_GENE_[' + minw_gene + ']'
            relation.add_feature(feature)
        if mini_hpo is not None:
            # feature = 'MIN_VERB_HPO_[' + minw_hpo + ']' + minp_hpo)
            # relation.add_feature(feature)
            feature = inv + 'MIN_VERB_HPO_[' + minw_hpo + ']'
            relation.add_feature(feature)

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
                relation.add_feature("SEP_BY_[while]")
            if "whereas" == sentence.words[i].lemma:
                relation.add_feature("SEP_BY_[whereas]")
            if sentence.words[i].lemma in ["no", "not", "neither", "nor"]:
                neg_word_index = i
        # Features for the negative words
        # TODO: We would probably need distant supervision for these
        if neg_word_index > -1:
            gene_p = None
            gene_l = 100
            for word in sentence.words[gene_start:gene_end+1]:
                p = sentence.get_word_dep_path(
                    word.in_sent_idx, neg_word_index)
                if len(p) > gene_l:
                    gene_p = p
                    gene_l = len(p)
            if gene_p:
                relation.add_feature(inv + "GENE_TO_NEG_[" + gene_p + "]")
            hpo_p = None
            hpo_l = 100
            for word in sentence.words[hpoterm_start:hpoterm_end+1]:
                p = sentence.get_word_dep_path(
                    word.in_sent_idx, neg_word_index)
                if len(p) > hpo_l:
                    hpo_p = p
                    hpo_l = len(p)
            if hpo_p:
                relation.add_feature(inv + "HPO_TO_NEG_[" + hpo_p + "]")
        # The sequence of lemmas between the two mentions and the sequence of
        # lemmas between the two mentions but using the NERs, if present.
        seq_list_ners = []
        seq_list_lemmas = []
        for word in sentence.words[betw_start+1:betw_end]:
            if word.ner != "O":
                seq_list_ners.append(word.ner)
            else:
                seq_list_ners.append(word.lemma)
            seq_list_lemmas.append(word.lemma)
        seq_ners = " ".join(seq_list_ners)
        seq_lemmas = " ".join(seq_list_lemmas)
        relation.add_feature(inv + "WORD_SEQ_[" + seq_lemmas + "]")
        relation.add_feature(inv + "WORD_SEQ_NER_[" + seq_ners + "]")
        # Shortest dependency path between the two mentions
        relation.add_feature(inv + "DEP_PATH_[" + sentence.dep_path(
            gene_mention, hpoterm_mention) + "]")
        # Number of words between the mentions
        # TODO I think this should be some kind of supervision rule instead?
        relation.add_feature(
            inv + "WORD_SEQ_LEN_[" + str(betw_end - betw_start - 1) + "]")
    # Lemmas on the left and on the right
    if gene_start > 0:
        relation.add_feature(
            "GENE_NGRAM_LEFT_1_[" + sentence.words[gene_start-1].lemma + "]")
    if gene_end < len(sentence.words) - 1:
        relation.add_feature(
            "GENE_NGRAM_RIGHT_1_[" + sentence.words[gene_end+1].lemma + "]")
    if hpoterm_start > 0:
        relation.add_feature(
            "HPO_NGRAM_LEFT_1_[" + sentence.words[hpoterm_start-1].lemma + "]")
    if hpoterm_end < len(sentence.words) - 1:
        relation.add_feature(
            "HPO_NGRAM_RIGHT_1_[" + sentence.words[hpoterm_end+1].lemma + "]")


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
                       "bounding_boxes", "gene_entities", "gene_wordidxss",
                       "gene_is_corrects", "gene_types",
                       "hpoterm_entities", "hpoterm_wordidxss",
                       "hpoterm_is_corrects", "hpoterm_types"],
                [no_op, int, lambda x: TSVstring2list(x, int), TSVstring2list,
                 TSVstring2list, TSVstring2list, TSVstring2list,
                 TSVstring2list, lambda x: TSVstring2list(x, int),
                 TSVstring2list,  # these are for the sentence
                 TSVstring2list, lambda x: TSVstring2list(x, sep="!~!"),
                 TSVstring2list, TSVstring2list,  # these are for the genes
                 TSVstring2list, lambda x: TSVstring2list(x, sep="!~!"),
                 TSVstring2list, TSVstring2list,  # these are for the HPO
                 ])
            # Remove the genes that are unsupervised copies
            supervised_idxs = set()
            unsupervised_idxs = set()
            for i in range(len(line_dict["gene_is_corrects"])):
                if line_dict["gene_is_corrects"][i] == "n":
                    unsupervised_idxs.add(i)
                else:
                    supervised_idxs.add(i)
            survived_unsuperv_idxs = set()
            for i in unsupervised_idxs:
                wordidxs = line_dict["gene_wordidxss"][i]
                found = False
                for j in supervised_idxs:
                    if line_dict["gene_wordidxss"][j] == wordidxs:
                        found = True
                        break
                if not found:
                    survived_unsuperv_idxs.add(i)
            to_keep = sorted(survived_unsuperv_idxs | supervised_idxs)
            new_gene_entities = []
            new_gene_wordidxss = []
            new_gene_is_corrects = []
            new_gene_types = []
            for i in to_keep:
                new_gene_entities.append(line_dict["gene_entities"][i])
                new_gene_wordidxss.append(line_dict["gene_wordidxss"][i])
                new_gene_is_corrects.append(line_dict["gene_is_corrects"][i])
                new_gene_types.append(line_dict["gene_types"][i])
            line_dict["gene_entities"] = new_gene_entities
            line_dict["gene_wordidxss"] = new_gene_wordidxss
            line_dict["gene_is_corrects"] = new_gene_is_corrects
            line_dict["gene_types"] = new_gene_types
            # Remove the hpoterms that are unsupervised copies
            supervised_idxs = set()
            unsupervised_idxs = set()
            for i in range(len(line_dict["hpoterm_is_corrects"])):
                if line_dict["hpoterm_is_corrects"][i] == "n":
                    unsupervised_idxs.add(i)
                else:
                    supervised_idxs.add(i)
            survived_unsuperv_idxs = set()
            for i in unsupervised_idxs:
                wordidxs = line_dict["hpoterm_wordidxss"][i]
                found = False
                for j in supervised_idxs:
                    if line_dict["hpoterm_wordidxss"][j] == wordidxs:
                        found = True
                        break
                if not found:
                    survived_unsuperv_idxs.add(i)
            to_keep = sorted(survived_unsuperv_idxs | supervised_idxs)
            new_hpoterm_entities = []
            new_hpoterm_wordidxss = []
            new_hpoterm_is_corrects = []
            new_hpoterm_types = []
            for i in to_keep:
                new_hpoterm_entities.append(line_dict["hpoterm_entities"][i])
                new_hpoterm_wordidxss.append(line_dict["hpoterm_wordidxss"][i])
                new_hpoterm_is_corrects.append(
                    line_dict["hpoterm_is_corrects"][i])
                new_hpoterm_types.append(line_dict["hpoterm_types"][i])
            line_dict["hpoterm_entities"] = new_hpoterm_entities
            line_dict["hpoterm_wordidxss"] = new_hpoterm_wordidxss
            line_dict["hpoterm_is_corrects"] = new_hpoterm_is_corrects
            line_dict["hpoterm_types"] = new_hpoterm_types
            # Create the sentence object where the two mentions appear
            sentence = Sentence(
                line_dict["doc_id"], line_dict["sent_id"],
                line_dict["wordidxs"], line_dict["words"], line_dict["poses"],
                line_dict["ners"], line_dict["lemmas"], line_dict["dep_paths"],
                line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Iterate over each pair of (gene,phenotype) mention
            for g_idx in range(len(line_dict["gene_is_corrects"])):
                g_wordidxs = TSVstring2list(
                    line_dict["gene_wordidxss"][g_idx], int)
                gene_mention = Mention(
                    "GENE", line_dict["gene_entities"][g_idx],
                    [sentence.words[j] for j in g_wordidxs])
                if line_dict["gene_is_corrects"][g_idx] == "n":
                    gene_mention.is_correct = None
                elif line_dict["gene_is_corrects"][g_idx] == "f":
                    gene_mention.is_correct = False
                elif line_dict["gene_is_corrects"][g_idx] == "t":
                    gene_mention.is_correct = True
                else:
                    assert False
                gene_mention.type = line_dict["gene_types"][g_idx]
                for h_idx in range(len(line_dict["hpoterm_is_corrects"])):
                    h_wordidxs = TSVstring2list(
                        line_dict["hpoterm_wordidxss"][h_idx], int)
                    hpoterm_mention = Mention(
                        "hpoterm", line_dict["hpoterm_entities"][h_idx],
                        [sentence.words[j] for j in h_wordidxs])
                    if line_dict["hpoterm_is_corrects"][h_idx] == "n":
                        hpoterm_mention.is_correct = None
                    elif line_dict["hpoterm_is_corrects"][h_idx] == "f":
                        hpoterm_mention.is_correct = False
                    elif line_dict["hpoterm_is_corrects"][h_idx] == "t":
                        hpoterm_mention.is_correct = True
                    else:
                        assert False
                    hpoterm_mention.type = line_dict["hpoterm_types"][h_idx]
                    # Skip if the word indexes overlab
                    if set(g_wordidxs) & set(h_wordidxs):
                        continue
                    relation = Relation(
                        "GENEHPOTERM", gene_mention, hpoterm_mention)
                    # Add features
                    add_features(relation, gene_mention, hpoterm_mention,
                                 sentence)
                    # Supervise
                    # One of the two mentions is labelled as False
                    if gene_mention.is_correct is False and \
                            hpoterm_mention.is_correct is not False:
                        relation.is_correct = False
                        relation.type = "GENEHPOTERM_SUP_F_G"
                    elif hpoterm_mention.is_correct is False and \
                            gene_mention.is_correct is not False:
                        relation.is_correct = False
                        relation.type = "GENEHPOTERM_SUP_F_H"
                    elif hpoterm_mention.is_correct is False and \
                            gene_mention.is_correct is False:
                        relation.is_correct = False
                        relation.type = "GENEHPOTERM_SUP_F_GH"
                    # Present in the existing HPO mapping
                    else:
                        in_mapping = False
                        hpo_entity_id = hpoterm_mention.entity.split("|")[0]
                        if frozenset([gene_mention.words[0].word, hpo_entity_id]) in \
                                genehpoterms_dict:
                            in_mapping = True
                        else:
                            for gene in gene_mention.entity.split("|"):
                                if frozenset([gene, hpo_entity_id]) in \
                                        genehpoterms_dict:
                                    in_mapping = True
                                    break
                        if in_mapping:
                            relation.is_correct = True
                            relation.type = "GENEHPOTERM_SUP_MAP"
                    # Print!
                    print(relation.tsv_dump())
