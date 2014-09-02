#! /usr/bin/env python3

import fileinput
import random

from dstruct.Mention import Mention
from dstruct.Sentence import Sentence
from dstruct.Relation import Relation
from helper.dictionaries import load_dict
from helper.easierlife import get_dict_from_TSVline, no_op, TSVstring2list

SUPERVISION_PROB = 0.5
SUPERVISION_GENEHPOTERMS_DICT_FRACTION = 0.4

## Perform distant supervision
def supervise(relation, gene_mention, hpoterm_mention, sentence):
    if random.random() < SUPERVISION_PROB and relation.bla in supervision_genehpoterms_dict:
        relation.is_correct = True


## Add features
def add_features(relation, gene_mention, hpoterm_mention, sentence):
    # Add features
    gene_start = int(gene_mention.id.split("_")[4])
    hpoterm_start = int(hpoterm_mention.id.split("_")[4])
    gene_end = int(gene_mention.id.split("_")[5])
    hpoterm_end = int(hpoterm_mention.id.split("_")[5])
    start = min(gene_start, hpoterm_start)
    end = max(gene_end, hpoterm_end)
    # Present in the existing HPO mapping
    relation.add_feature("IN_GENE_HPOTERM_MAP={}".format(int(frozenset([gene_mention.symbol,
        hpoterm_mention.term.lower()]) in genehpoterms_dict)))
    # Verb between the two words, if present
    # XXX (Matteo) From pharm, RelationExtractor_Druggene_mention.py, but not correct
    #for word in sentence.words[start:end]: 
    #    if re.search('^VB[A-Z]*$', word.pos):
    #        relation.add_feature("verb="+word.lemma])
    # Word sequence between words
    relation.add_feature("word_seq="+"_".join([w.lemma for w in sentence.words[start:end]]))
    # Left and right windows
    if start > 0:
        relation.add_feature("WINDOW_LEFT_1={}".format(sentence.words[start-1]))
    if end < len(sentence.words) - 1:
        relation.add_feature("WINDOW_RIGHT_1={}".format(sentence.words[end]))
    # Shortest dependency path between the two mentions
    relation.add_feature(sentence.dep_path(gene_mention, hpoterm_mention))


# Load the gene<->hpoterm dictionary
genehpoterms_dict = load_dict("genehpoterms")
# Create supervision dictionary that only contains a fraction of the genes in the gene
# dictionary. This is to avoid that we label as positive examples everything
# that is in the dictionary
supervision_genehpoterms_dict = dict()
to_sample = set(random.sample(range(len(genehpoterms_dict)),
        int(len(genehpoterms_dict) * SUPERVISION_GENEHPOTERMS_DICT_FRACTION)))
i = 0
for hpoterm in genehpoterms_dict:
    if i in to_sample:
        supervision_genehpoterms_dict[hpoterm] = genehpoterms_dict[hpoterm]
    i += 1

if __name__ == "__main__":
    # Process input
    with fileinput.input as input_files:
        for line in input_files:
            # This is for json
            #line_dict = json.loads(line)
            # This is for tsv
            line_dict = get_dict_from_TSVline(line, [ "doc_id", "sent_id", "wordidxs",
            "words", "poses", "ners", "lemmas", "dep_paths", "dep_parents",
            "bounding_boxes", "gene_entity", "gene_wordidxs", "hpoterm_entity",
            "hpoterm_wordidxs"], [no_op, int, lambda x :
                TSVstring2list(x, int), TSVstring2list, TSVstring2list,
                TSVstring2list, TSVstring2list, TSVstring2list, lambda x :
                TSVstring2list(x, int), TSVstring2list, no_op, lambda x:
                TSVstring2list(x, int), no_op, lambda x : TSVstring2list(x, int)])
            # Create the sentence object where the two mentions appear
            sentence = Sentence(line_dict["doc_id"], line_dict["sent_id"], line_dict["wordidxs"],
                    line_dict["words"], line_dict["poses"], line_dict["ners"], line_dict["lemmas"],
                    line_dict["dep_paths"], line_dict["dep_parents"], line_dict["bounding_boxes"])
            # Create the mentions
            gene_mention = Mention("GENE", line_dict["gene_entity"],
                    [sentence.words[i] for i in line_dict["gene_wordidxs"]])
            hpoterm_mention = Mention("HPOTERM", line_dict["hpoterm_entity"],
                    [sentence.words[i] for i in line_dict["hpoterm_wordidxs"]])
            # Create the relation
            relation = Relation("GENEHPOTERM", gene_mention, hpoterm_mention)
            # Add features
            add_features(relation, gene_mention, hpoterm_mention, sentence)
            # Supervise
            supervise(relation, gene_mention, hpoterm_mention, sentence)
            # Print!
            # This is for json
            #print(relation.json_dump())
            # This is for tsv
            print(relation.tsv_dump())

