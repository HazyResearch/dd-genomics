#! /usr/bin/env python3

import fileinput

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2list

# Load the gene<->hpoterm dictionary
genehpoterms_dict = load_dict("genehpoterms")


# Supervise the candidates
def supervise(relation, gene_mention, hpoterm_mention, sentence):
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
    else:
        # Present in the existing HPO mapping
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
            # Remove the genes that are unsupervised copies or duplicates
            supervised_idxs = set()
            unsupervised_idxs = set()
            for i in range(len(line_dict["gene_is_corrects"])):
                if line_dict["gene_is_corrects"][i] == "n":
                    unsupervised_idxs.add(i)
                else:
                    if line_dict["gene_types"][i] != "GENE_SUP_contr_2":
                        # The above condition is to avoid duplicates
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
            # Skip weird sentences
            if sentence.is_weird():
                continue
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
                assert not gene_mention.type.endswith("_UNSUP")
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
                    assert not hpoterm_mention.type.endswith("_UNSUP")
                    # Skip if the word indexes overlab
                    if set(g_wordidxs) & set(h_wordidxs):
                        continue
                    # Skip if the mentions are too far away
                    gene_start = gene_mention.wordidxs[0]
                    hpoterm_start = hpoterm_mention.wordidxs[0]
                    gene_end = gene_mention.wordidxs[-1]
                    hpoterm_end = hpoterm_mention.wordidxs[-1]
                    limits = sorted(
                        (gene_start, hpoterm_start, gene_end, hpoterm_end))
                    start = limits[0]
                    betw_start = limits[1]
                    betw_end = limits[2]
                    if betw_end - betw_start > 50:
                        continue
                    relation = Relation(
                        "GENEHPOTERM", gene_mention, hpoterm_mention)
                    # Supervise
                    supervise(relation, gene_mention, hpoterm_mention,
                              sentence)
                    # Print!
                    print(relation.tsv_dump())
